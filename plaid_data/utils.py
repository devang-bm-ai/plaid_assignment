import plaid
from django.conf import settings
from datetime import datetime, timedelta


def get_plaid_client():
    client = plaid.Client(client_id=settings.PLAID_CLIENT_ID, secret=settings.PLAID_SECRET, environment=settings.PLAID_ENV)
    return client


def get_date_n_days_ago(num_days):
    today = datetime.now()
    n_days_ago = today - timedelta(days=num_days)
    return n_days_ago.strftime('%Y-%m-%d')