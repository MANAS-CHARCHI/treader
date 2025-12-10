import requests
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
import json
import urllib
from rest_framework_simplejwt.tokens import RefreshToken
from .jwt_cookies import set_jwt_cookies
import os
from dotenv import load_dotenv
load_dotenv()

def save_user_profile(strategy, details, backend, user=None, response=None, *args, **kwargs):
    if user:
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
        "name": user.first_name+" "+user.last_name,
        "avatar": avatar,
    }

    # Redirect URL (frontend)
     # Adjust as needed
    redirect_url = os.getenv("REDIRECT_AFTER_SOCIAL_AUTH") + urllib.parse.quote(json.dumps(user_data))

    # Build Django response object
    response = HttpResponseRedirect(redirect_url)
    response = set_jwt_cookies(
        response,
        refresh,
        access,
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