"""Auth app URLs"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CustomTokenObtainPairView, LogoutView, RevokeAllUserTokensView

app_name = 'auth'

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/users/<int:user_id>/revoke-tokens/', RevokeAllUserTokensView.as_view(), name='revoke_tokens'),
]
