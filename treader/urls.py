from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/markets/', include('markets.urls')),
    path('api/trading/', include('trading.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/realtime/', include('realtime.urls')),
]