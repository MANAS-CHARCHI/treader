import json
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

from google.oauth2 import id_token
from google.auth.transport import requests
from .jwt_cookies import set_jwt_cookies
from django.conf import settings

class GoogleAuthAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token missing"}, status=400)

        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            )

            email = idinfo.get("email")
            picture = idinfo.get("picture")

            if not email:
                return Response({"error": "No email from Google"}, status=400)

            # Create / get user
            user, _ = User.objects.get_or_create(
                email=email,
            )

            # Generate JWT
            refresh = RefreshToken.for_user(user)
            response = Response({
                    "user": {
                        "email": user.email,
                        "name": user.first_name + " " + user.last_name,
                        "avatar": picture,
                    },
                },
                status=status.HTTP_200_OK
            )
            response = set_jwt_cookies(response, refresh, refresh.access_token)

            return response

        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)
        
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
        if user and not user.login_method == 'email':
            method = user.login_method.split('-')[0]
            return Response(
                {"error": f"Password is not set by you, Please log in using {method or user.login_method}."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
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
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            user.last_login = timezone.now()
            user.save()
            response = Response(
                {"user": {
                        "email": user.email,
                        "name": user.first_name + " " + user.last_name,
                        "avatar": user.avatar,
                    },
                },
                status=status.HTTP_200_OK
            )
            response = set_jwt_cookies(response, refresh, refresh.access_token)
                
            return response
        else:
            return Response(
                {"error": "Invalid email/username or password."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class LogOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=401)

        response = Response({"message": "Token refreshed"}, status=200)

        response = set_jwt_cookies(response, refresh, new_access)

        return response
    
class TestValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = User.objects.get(email=request.user.email)
            return Response({'user is valid'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # No existing user, social pipeline will create a new one
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)




import requests
import yfinance as yf
class PrintStockDataView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, symbol):
        # Example symbols:
        # NSE → RELIANCE.NS
        # BSE → 500325.BO
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info  # Fast & lightweight data

            data = {
                "symbol": symbol,
                "last_price": info.last_price,
                "open": info.open,
                "day_high": info.day_high,
                "day_low": info.day_low,
                "previous_close": info.previous_close,
                "volume": info.last_volume,
                "exchange": info.get("exchange", "NSE/BSE"),
                "currency": info.currency,
            }

            return Response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)