from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import OTPRequestSerializer, OTPVerifySerializer, LoginResponseSerializer, RegisterSerializer
from apps.users.serializers import UserSerializer
from apps.users.models import UserRole


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


class RegisterView(APIView):
    """Full user registration with username, mobile, password, role & details."""
    permission_classes = []

    @extend_schema(request=RegisterSerializer, responses={201: LoginResponseSerializer})
    def post(self, request):
        import re
        from django.db import IntegrityError

        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            # Extract first error or join field errors into readable string
            errors = {}
            for field, err_list in serializer.errors.items():
                msg = err_list[0] if isinstance(err_list, list) and err_list else str(err_list)
                errors[field] = msg
            first_msg = next(iter(errors.values())) if errors else "Invalid registration data"
            return Response({'detail': first_msg, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        username = data['username'].strip()
        raw_mobile = data['mobile'].strip()
        # Clean mobile number: keep digits, extract 10-digit number if longer (e.g. +91)
        digits_only = re.sub(r'\D', '', raw_mobile)
        mobile = digits_only[-10:] if len(digits_only) >= 10 else digits_only
        password = data['password']
        role_str = data.get('role', 'PILGRIM').upper()

        # 1. Check Username existence (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            return Response(
                {'detail': f"उपयोगकर्ता नाव '{username}' आधीच वापरात आहे. कृपया दुसरं नाव निवडा. (Username '{username}' is already taken.)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Check Mobile number existence
        if User.objects.filter(mobile=mobile).exists():
            return Response(
                {'detail': f"मोबाईल नंबर '{mobile}' आधीच नोंदणीकृत आहे. (Mobile number '{mobile}' is already registered.)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate role against UserRole
        valid_roles = [choice[0] for choice in UserRole.choices]
        if role_str not in valid_roles:
            role_str = UserRole.PILGRIM

        try:
            user = User.objects.create(
                username=username,
                mobile=mobile,
                role=role_str,
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                email=data.get('email', ''),
                is_verified=True,
            )
            user.set_password(password)
            user.save()
        except IntegrityError as ie:
            err_str = str(ie).lower()
            if 'username' in err_str:
                return Response({'detail': 'उपयोगकर्ता नाव आधीच वापरले आहे (Username already taken).'}, status=status.HTTP_400_BAD_REQUEST)
            elif 'mobile' in err_str:
                return Response({'detail': 'हा मोबाईल नंबर आधीच नोंदणीकृत आहे (Mobile number already registered).'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'नोंदणी अयशस्वी झाली. माहिती पुन्हा तपासा. (Registration failed. Please check details.)'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


