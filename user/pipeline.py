import requests
from django.core.files.base import ContentFile
def save_user_profile(strategy, details, backend, user=None, response=None, *args, **kwargs):
    if user:
        print("Saving user profile...", details)
        user.first_name = details.get('first_name', user.first_name)
        user.last_name = details.get('last_name', user.last_name)

        user.avatar = response.get('picture') or details.get('picture')
        user.is_active = True
        user.save()
    
import json

import urllib
from rest_framework_simplejwt.tokens import RefreshToken
def generate_tokens_and_redirect(strategy, backend, user=None, details=None, response=None, *args, **kwargs):
    if user is None:
        return

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    avatar = None
    if response:
        avatar = response.get('picture')  # Google returns 'picture' in profile info
    if not avatar and details:
        avatar = details.get('picture')
    user={
        "email": user.email,
        "name": user.first_name,
        "avatar": avatar,
    }
    user_json = urllib.parse.quote(json.dumps(user))
    redirect_url = f"http://localhost:5173/auth/success?access={access}&refresh={refresh}&user={user_json}"

    return strategy.redirect(redirect_url)