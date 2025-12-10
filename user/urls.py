from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import UserRegistrationView, UserActivationView, UserLoginView, GoogleAuthAPIView, LogOutView, TestValidateView

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='user-register'),
    path('auth/google/', GoogleAuthAPIView.as_view()),
    path('activate/<str:email>/<str:activation_code>', UserActivationView.as_view(), name='user-activate'),
    path('login', UserLoginView.as_view(), name='user-login'),
    path('logout', LogOutView.as_view(), name='user-logout'),
    path('test-validate', TestValidateView.as_view(), name='test-validate'),

]
