from .base import RequestModel, BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from users.models import User

#
# def get_default_list():
#     return list


class Token(RequestModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public_token = models.CharField(max_length=64, default='')
    access_token = models.CharField(max_length=64, default='')
    item_id = models.CharField(max_length=64, default='')
    is_active = models.BooleanField(default=True)


class Item(RequestModel):
    class ProductTypes(models.TextChoices):
        AUTH = "auth", _("Authentication")
        IDENTITY = "identity", _("Identity")
        BALANCE = "balance", _("Balance")
        CREDIT_DETAILS = "credit_details", _("Credit Details")
        TRANSACTIONS = "transactions", _("Transactions")
        ITEM = "item", _("item")
        INCOME = "income", _("income")
        ASSETS = "assets", _("assets")
        HOLDINGS = "holdings", _("holdings")
        INVESTMENTS = "investments", _("investments")
        LIABILITIES = "liabilities", _("liabilities")

    item_id = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    available_products = ArrayField(models.CharField(max_length=32, choices=ProductTypes.choices,null=True, blank=True), size=10, default=list, blank=True, null=True)
    billed_products = ArrayField(models.CharField(max_length=32,  choices=ProductTypes.choices, null=True, blank=True), size=10, default=list, blank=True, null=True)

    institution_id = models.CharField(max_length=32, null=True, blank=True)

    webhook = models.URLField(null=True, blank=True)
    relink_status = models.CharField(max_length=256, null=True, blank=True)

    status = models.JSONField(null=True, blank=True)
    error = models.JSONField(null=True, blank=True)


class Account(RequestModel):
    class AccountTypes(models.TextChoices):
        INVESTMENT = 'investment', _('Investment')
        CREDIT = 'credit', _('Credit Card')
        DEPOSITORY = 'depository', _('Depository Account')
        LOAN = 'loan', _('Loan Account')
        OTHER = 'other', _('Non specified account type')

    account_id = models.CharField(max_length=64)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    balances = models.JSONField(null=True, blank=True)
    mask = models.CharField(max_length=6, null=True, blank=True)

    name = models.CharField(max_length=256, null=True, blank=True)
    official_name = models.CharField(max_length=512, null=True, blank=True)

    type = models.CharField(max_length=32, choices=AccountTypes.choices)
    subtype = models.CharField(max_length=256)


class Transaction(RequestModel):
    class TransactionCodes(models.TextChoices):
        ADJUSTMENT = 'adjustment', _('Adjustment')
        ATM = 'atm', _('Atm')
        BANK = 'bank', _('Bank')
        CHARGE = 'charge', _('Charge')
        BILL_PAYMENT = 'bill payment', _('Bill payment')
        CASH = 'cash', _('Cash')
        CASHBACK = 'cashback', _('Cashback')
        CHEQUE = 'cheque', _('Cheque')
        DIRECT = 'direct debit', _('Direct')
        INTEREST = 'interest', _('Interest')
        PURCHASE = 'purchase', _('Purchase')
        STANDING_ORDER = 'standing order', _('Standing Order')
        TRANSFER = 'transfer', _('Transfer')

    transaction_id = models.CharField(max_length=64)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=256, null=True)

    pending_transaction_id = models.CharField(max_length=64, null=True)
    pending = models.BooleanField(default=False)

    payment_channel = models.CharField(max_length=32, null=True, blank=True)
    payment_processor = models.CharField(max_length=64, null=True, blank=True)
    payment_meta = models.JSONField(null=True, blank=True)

    name = models.CharField(max_length=255, null=True, blank=True)
    merchant_name = models.CharField(max_length=255, null=True, blank=True)

    location = models.JSONField(null=True, blank=True)

    date = models.DateField(null=True, blank=True)
    authorized_date = models.DateField(null=True, blank=True)

    category_id = models.CharField(max_length=24, null=True, blank=True)
    category = ArrayField(models.CharField(max_length=256, null=True, blank=True), size=10, default=list, null=True, blank=True)

    iso_currency_code = models.CharField(max_length=16, null=True, blank=True)
    unofficial_currency_code = models.CharField(max_length=16, null=True, blank=True)

    amount = models.DecimalField(max_digits=64, decimal_places=6)

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_code = models.CharField(max_length=32, choices=TransactionCodes.choices, null=True, blank=True)


class TransactionWebhook(BaseModel):
    class WebhookTypes(models.TextChoices):
        TRANSACTIONS = 'TRANSACTIONS', _("Transactions")

    class WebhookCode(models.TextChoices):
        INITIAL_UPDATE = 'INITIAL_UPDATE', _("Initial Update")
        HISTORICAL_UPDATE = 'HISTORICAL_UPDATE', _("Historical Update")
        DEFAULT_UPDATE = 'DEFAULT_UPDATE', _("Default Update")
        TRANSACTIONS_REMOVED = 'TRANSACTIONS_REMOVED', _("Transactions removed")

    webhook_type = models.CharField(max_length=20, null=True, blank=True, choices=WebhookTypes.choices, default=WebhookTypes.TRANSACTIONS)
    webhook_code = models.CharField(max_length=20, null=True, blank=True, choices=WebhookCode.choices)

    item_id = models.CharField(max_length=64)

    error = models.TextField(null=True, blank=True)
    new_transactions = models.IntegerField(null=True, blank=True)
    removed_transactions = ArrayField(models.CharField(max_length=64, blank=True, null=True), size=200, null=True, blank=True)



