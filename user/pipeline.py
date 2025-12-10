import requests
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
import json
import urllib
from rest_framework_simplejwt.tokens import RefreshToken

def save_user_profile(strategy, details, backend, user=None, response=None, *args, **kwargs):
    if user:
        print("Saving user profile...", details)
        user.first_name = details.get('first_name', user.first_name)
        user.last_name = details.get('last_name', user.last_name)

        user.avatar = response.get('picture') or details.get('picture')
        user.is_active = True
        user.save()
    
def generate_tokens_and_redirect(strategy, backend, user=None, details=None, response=None, *args, **kwargs):
    if user is None:
        return
    
    # Create JWT tokens
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    # Prepare user info (optional)
    avatar = None
    if response:
        avatar = response.get("picture")
    if not avatar and details:
        avatar = details.get("picture")

    user_data = {
        "email": user.email,
        "name": user.first_name,
        "avatar": avatar,
    }

    # Redirect URL (frontend)
    redirect_url = "http://localhost:5173/auth/success"

    # Build Django response object
    response = HttpResponseRedirect(redirect_url)

    # -------------------------------
    # SET SECURE HTTP-ONLY COOKIES
    # -------------------------------

    # Access token cookie
    response.set_cookie(
        "access_token",
        str(access),
        httponly=True,
        secure=False,  # Set to True in production (HTTPS)
        samesite="Lax",  # Or "None" if using HTTPS with cross-site
        max_age=3600,  # 1 hour
    )

    # Refresh token cookie
    response.set_cookie(
        "refresh_token",
        str(refresh),
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=7 * 24 * 3600,  # 7 days
    )

    # Optional: user profile info cookie (NOT httpOnly)
    response.set_cookie(
        "user_info",
        urllib.parse.quote(json.dumps(user_data)),
        httponly=False,  # readable by frontend
        secure=False,
        samesite="Lax",
        max_age=7 * 24 * 3600,
    )

    return response

from django.contrib.auth import get_user_model

User = get_user_model()
def associate_by_email(strategy, details, backend, uid, user=None, *args, **kwargs):
    """
    If a user with the same email exists, associate this social account with them.
    Allows the user to log in via social auth even if they registered with
    normal email/password.
    """
    if user:
        # User is already authenticated, nothing to do
        return {'user': user}

    email = details.get('email')
    if not email:
        # No email provided, cannot associate
        return

    try:
        # Look for an existing user with the same email
        existing_user = User.objects.get(email=email)

        # Associate this social account with the existing user
        backend.strategy.storage.user.changed(existing_user)

        # Return the existing user so pipeline continues with them
        return {'user': existing_user}

    except User.DoesNotExist:
        # No existing user, social pipeline will create a new one
        return