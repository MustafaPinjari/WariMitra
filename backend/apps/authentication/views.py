from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import OTPRequestSerializer, OTPVerifySerializer, LoginResponseSerializer
from apps.users.serializers import UserSerializer

User = get_user_model()

class SendOTPView(APIView):
    permission_classes = []

    @extend_schema(request=OTPRequestSerializer, responses={200: dict})
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            # In a real app, integrate with SMS gateway. For now, simulate.
            return Response({"message": "OTP sent successfully (Simulated: 123456)"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = []

    @extend_schema(request=OTPVerifySerializer, responses={200: LoginResponseSerializer})
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            
            # Simple mock verification
            if otp == '123456':
                user, created = User.objects.get_or_create(
                    mobile=mobile,
                    defaults={'username': mobile}
                )
                
                if created:
                    user.set_unusable_password()
                    user.is_verified = True
                    user.save()
                    
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
                
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginWithUserView(APIView):
    """Username/password login that returns tokens + full user object."""
    permission_classes = []

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials. Check username and password.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)
