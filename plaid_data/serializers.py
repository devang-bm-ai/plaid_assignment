from rest_framework import serializers
from .models.models import Token, Item, Account, Transaction, TransactionWebhook


class TokenRequestSerializer(serializers.Serializer):
    public_token = serializers.CharField(max_length=64, allow_blank=False, allow_null=False)


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        # fields = '__all__'
        exclude = ['item_id']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        # fields = '__all__'
        exclude = ['account_id']


class TransactionWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionWebhook
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        # fields = '__all__'
        exclude = ['transaction_id']
