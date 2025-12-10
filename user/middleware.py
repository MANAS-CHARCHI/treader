from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from .jwt_cookies import set_jwt_cookies
class AutoRefreshTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access = request.COOKIES.get("access_token")
        refresh = request.COOKIES.get("refresh_token")

        # Try validate access token first
        access_valid = False
        if access:
            try:
                AccessToken(access)
                access_valid = True
            except TokenError:
                access_valid = False

        # If access invalid but refresh exists → refresh it
        if not access_valid and refresh:
            try:
                refresh_token = RefreshToken(refresh)
                new_access = str(refresh_token.access_token)

                # Optionally rotate refresh token if enabled
                new_refresh = None
                if getattr(refresh_token, 'BLACKLIST_AFTER_ROTATION', False):
                    refresh_token.blacklist()
                    # You can create a new refresh token if needed:
                    # new_refresh_token = RefreshToken.for_user(user)
                    # new_refresh = str(new_refresh_token)

                request.new_access_token = new_access
                if new_refresh:
                    request.new_refresh_token = new_refresh

                # IMPORTANT: override the Authorization header for DRF authentication
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access}'

            except TokenError:
                request.clear_auth_cookies = True

        # Continue processing the request normally
        response = self.get_response(request)

        response = set_jwt_cookies(
            response,
            getattr(request, "new_refresh_token", None),
            getattr(request, "new_access_token", None),
            set_access=hasattr(request, "new_access_token"),
            set_refresh=hasattr(request, "new_refresh_token"),
        )

        # Clear cookies if both tokens invalid
        if hasattr(request, "clear_auth_cookies"):
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

        return response
