from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, BasicAuthentication

from django.core.exceptions import ImproperlyConfigured

from plaid.errors import APIError, PlaidError

from .models.models import Token
from .serializers import TokenRequestSerializer, TokenSerializer, AccountSerializer, TransactionSerializer, TransactionWebhookSerializer
from .utils import get_plaid_client
from .tasks import get_item_and_account_metadata, handle_transaction_update_webhook
from .models.models import Account, Transaction, TransactionWebhook, Item


# Create your views here.
class TokenViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, BasicAuthentication, ]
    serializer_class = TokenSerializer
    serializer_classes = {
        'get_access_token': TokenRequestSerializer,
    }

    @action(methods=['POST', ], detail=False)
    def get_access_token(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid()
            validated_data = serializer.validated_data

            public_token = validated_data['public_token']
            exchange_response = get_plaid_client().Item.public_token.exchange(public_token)

            access_token = exchange_response['access_token']
            item_id = exchange_response['item_id']
            request_id = exchange_response['request_id']
            exchange_response.update({'public_token': public_token})
            if access_token and item_id:
                token, created = Token.objects.update_or_create(user=self.request.user, item_id = item_id, defaults=exchange_response)
                get_item_and_account_metadata.delay(token.id)
                return Response({'success': 'Access Token received'}, status=status.HTTP_200_OK)
        except APIError as e:
            return Response({})

        except PlaidError as e:
            return Response({'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET', ], detail=False)
    def get_public_token(self, request):

        res = get_plaid_client().Sandbox.public_token.create(
            "ins_3",
            ['transactions']
        )

        return Response(data=res, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Account.objects.filter(item__user=user)
        return queryset


class TransactionsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    serializer_class = TransactionSerializer
    serializer_classes = {
        'webhook': TransactionWebhookSerializer
    }

    @action(methods=['POST', ], detail=False)
    def webhook(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid()

        validated_data = serializer.validated_data

        transaction_webhook = TransactionWebhook.objects.create(**validated_data)

        handle_transaction_update_webhook.delay(validated_data)

        return Response({'success': 'Webhook received'}, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(item__user=user).order_by('-date')
        return queryset

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()