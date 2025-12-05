from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login
from .models import User, UserActivation
from .serializer import UserSerializer
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
  
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            UserActivation.objects.create(
                user=serializer.instance
            )
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserActivationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email=kwargs.get('email')
        activation_code=kwargs.get('activation_code')
        try:
            user=User.objects.get(email=email)
            activation=UserActivation.objects.get(user=user)
            if user.is_active:
                return Response({"message": "Account already activated."}, status=status.HTTP_200_OK)
            if activation.activation_code != activation_code:
                return Response({"error": "Invalid activation code."}, status=status.HTTP_400_BAD_REQUEST)
            if activation.is_expired():
                return Response({"error": "Activation code has expired."}, status=status.HTTP_400_BAD_REQUEST)
            user.is_active=True
            user.save()
            activation.activated_at=timezone.now()
            activation.save()
            return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Activation failed."}, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data=request.data
        login_identifier = data.get('username') or data.get('email')
        password=data.get('password')
        if not login_identifier or not password:
             return Response(
                {"error": "Please provide both an email/username and a password."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(email=login_identifier).first() or User.objects.filter(username=login_identifier).first()
        if user and not check_password(password, user.password):
            return Response(
                {"error": "Invalid email/username or password."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        if user is not None:
            if not user.is_active:
                return Response(
                    {"error": "Account is not activated. Please check your email for the activation link."}, 
                    status=status.HTTP_403_FORBIDDEN 
                )
            refresh = RefreshToken.for_user(user)
            login(request, user)
            user.last_login = timezone.now()
            user.save()

            return Response(
                {
                    "message": f"Login successful for {user.email}.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid email/username or password."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )