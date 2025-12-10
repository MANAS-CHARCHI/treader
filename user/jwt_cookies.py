import os
from rest_framework.response import Response
from dotenv import load_dotenv
load_dotenv()
def set_jwt_cookies(
    response: Response,
    refresh=None,
    access=None,
    *,
    set_access=True,
    set_refresh=True,
    domain=os.getenv("DOMAIN_FOR_COOKIES")
):
    """
    Flexible cookie helper for:
    - access only
    - refresh only
    - both access + refresh

    Params:
        refresh: RefreshToken object or string
        access: Access token string
        set_access: whether to set access cookie
        set_refresh: whether to set refresh cookie
    """

    # -------------------
    # Set Access Token
    # -------------------
    if set_access:
        # if access token is not provided, but refresh exists → use refresh.access_token
        token_value = str(access or (refresh.access_token if refresh else ""))

        response.set_cookie(
            key="access_token",
            value=token_value,
            httponly=True,
            secure=False,   # change in prod
            samesite="Lax",
            domain=domain,
            path="/",
            max_age=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) * 60,  # in seconds
        )

    # -------------------
    # Set Refresh Token
    # -------------------
    if set_refresh and refresh:
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,   # change in prod
            samesite="Lax",
            domain=domain,
            path="/",
            max_age=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")) * 60,  # in seconds
        )

    return response
