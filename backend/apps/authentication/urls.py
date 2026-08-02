from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SendOTPView, VerifyOTPView, LoginWithUserView, RegisterView

urlpatterns = [
    # Standard JWT token endpoint (username/password → access+refresh)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Enhanced login — returns tokens + user object (used by Flutter app)
    path('login/', LoginWithUserView.as_view(), name='auth_login'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

