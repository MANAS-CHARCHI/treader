from django.contrib import admin
from django.urls import path
from django.urls import include


from django.http import JsonResponse
def login_error_view(request):
    return JsonResponse({"error": "Google login failed"}, status=400)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/google/', include('social_django.urls', namespace='social')),
    path('login-error/', login_error_view, name='login-error'),
    path('api/user/', include('user.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/markets/', include('markets.urls')),
    path('api/trading/', include('trading.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/realtime/', include('realtime.urls')),
]