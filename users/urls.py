from rest_framework import routers

from .views import AuthViewSet

users_router = routers.DefaultRouter(trailing_slash=False)
users_router.register('auth', AuthViewSet, basename='auth')

