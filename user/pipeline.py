def save_user_profile(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        user.first_name = details.get('first_name', user.first_name)
        user.last_name = details.get('last_name', user.last_name)
        user.avatar = details.get('picture', user.avatar)
        user.is_active = True  # Social login users usually verified
        user.save()