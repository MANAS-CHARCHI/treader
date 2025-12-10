from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Read access token from cookies
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
        except Exception:
            return None
        return self.get_user(validated_token), validated_token