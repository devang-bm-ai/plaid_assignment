from plaid_assignment.celery import app
from django.db import transaction
from .models.models import Token, Item, Account, Transaction
from .utils import get_plaid_client, get_date_n_days_ago
from .serializers import TokenSerializer, AccountSerializer, ItemSerializer, TransactionSerializer, TransactionWebhookSerializer
from plaid.errors import APIError, AuthError, PlaidError, PlaidCause, PLAID_ERROR_TYPE_MAP, BaseError


@app.task(name="get_item_and_account_metadata", bind=True)
def get_item_and_account_metadata(self, token_id):
    client = get_plaid_client()
    token = Token.objects.get(id=token_id)

    if token:
        try:
            item_response = client.Item.get(token.access_token)
            item_response.update(item_response["item"])
            item_response.update({'user': token.user_id})
            if item_response:
                serializer = ItemSerializer(data = item_response)
                serializer.is_valid()
                item_validated_data = dict(serializer.validated_data)
                item, created = handle_item_atomic(item_response)

                accounts_response = client.Accounts.get(token.access_token)
                if accounts_response:
                    for account_data in accounts_response["accounts"]:
                        account_data.update({"request_id": accounts_response["request_id"], 'item': item.id})
                        serializer = AccountSerializer(data=account_data)
                        serializer.is_valid()

                        account, created = handle_account_atomic(account_data)

                get_transactions_data.delay(item.item_id, get_date_n_days_ago(670) , get_date_n_days_ago(0))
        except APIError as e:
            raise self.retry(exc=e)
        except PlaidError as e:
            print(e.message)


@app.task(name="get_transaction_data", bind=True)
def get_transactions_data(self, item_id, start_date, end_date):
    client = get_plaid_client()
    item = Item.objects.get(item_id = item_id)
    token = Token.objects.get(item_id=item_id)

    if token:
        try:
            offset = 0
            transactions_to_fetch = True
            while transactions_to_fetch:
                transactions_response = client.Transactions.get(
                    token.access_token,
                    start_date,
                    end_date,
                    offset=offset
                )
                transactions = transactions_response["transactions"]

                for transaction_data in transactions:
                    account = Account.objects.get(account_id=transaction_data["account_id"])
                    transaction_data.update({"request_id": transactions_response["request_id"], "item": item.id,
                                             "account": account.id})
                    serializer = TransactionSerializer(data=transaction_data)
                    serializer.is_valid()
                    transaction_obj, created = handle_transaction_atomic(transaction_data)
                    print(transaction_obj)

                if offset + len(transactions) == transactions_response["total_transactions"]:
                    transactions_to_fetch = False
                else:
                    offset += len(transactions)

        except APIError as e:
            raise self.retry(exc=e)
        except PlaidError as e:
            print(e.message)


@app.task(name="handle_transaction_update_webhook", bind=True)
def handle_transaction_update_webhook(self, transaction_webhook):
    serializer = TransactionWebhookSerializer(data=transaction_webhook)
    serializer.is_valid()
    webhook_validated_data = serializer.validated_data
    if webhook_validated_data["webhook_type"] == 'TRANSACTIONS':
        if webhook_validated_data["webhook_code"] == 'INITIAL_UPDATE':
            print(get_date_n_days_ago(0))
            print(get_date_n_days_ago(30))
            get_transactions_data.delay(webhook_validated_data["item_id"], get_date_n_days_ago(30), get_date_n_days_ago(0))
        elif webhook_validated_data["webhook_code"] == 'HISTORICAL_UPDATE':
            get_transactions_data.delay(webhook_validated_data["item_id"], get_date_n_days_ago(670), get_date_n_days_ago(0))
        elif webhook_validated_data["webhook_code"] == 'DEFAULT_UPDATE':
            # Fetch last transaction dates
            get_transactions_data.delay(webhook_validated_data["item_id"], get_date_n_days_ago(14), get_date_n_days_ago(0))
        elif webhook_validated_data["webhook_code"] == 'TRANSACTIONS_REMOVED':
            pass


@transaction.atomic
def remove_transactions():
    pass



@transaction.atomic
def handle_account_atomic(account_data):
    serializer = AccountSerializer(data=account_data)
    serializer.is_valid(raise_exception=True)
    account_validated_data = dict(serializer.validated_data)

    print(account_validated_data)
    account_id = account_data['account_id']
    account, created = Account.objects.update_or_create(account_id=account_id, defaults=account_validated_data)

    return account, created


@transaction.atomic
def handle_item_atomic(item_data):
    serializer = ItemSerializer(data = item_data)
    serializer.is_valid()
    item_validated_data = dict(serializer.validated_data)

    item_id = item_data['item_id']

    item, created = Item.objects.update_or_create(defaults=item_validated_data, item_id=item_id)

    return item, created


@transaction.atomic
def handle_transaction_atomic(transaction_data):
    serializer = TransactionSerializer(data = transaction_data)
    serializer.is_valid(raise_exception=True)
    transaction_validated_data = dict(serializer.validated_data)

    transaction_id = transaction_data['transaction_id']

    transaction_obj, created = Transaction.objects.update_or_create(defaults=transaction_validated_data, transaction_id=transaction_id)

    return transaction_obj, created
