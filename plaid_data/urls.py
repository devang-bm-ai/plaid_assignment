from rest_framework import routers

from .views import TokenViewSet, AccountViewSet, TransactionsViewSet

plaid_data_router = routers.DefaultRouter(trailing_slash=False)
plaid_data_router.register('token/plaid', TokenViewSet, basename='token')
plaid_data_router.register('accounts', AccountViewSet, basename='accounts')
plaid_data_router.register('transactions', TransactionsViewSet, basename='transactions')

