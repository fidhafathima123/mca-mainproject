# accounts/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import *
app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.GuardianRegistrationView.as_view(), name='register'),
    path('login-redirect/', views.login_redirect, name='login_redirect'),
    path('logout/get/', LogoutView.as_view(), name='logout_get'),  # Allow GET request
       path('password-reset/', 
         CustomPasswordResetView.as_view(), 
         name='password_reset'),
    path('password-reset/done/', 
         CustomPasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         CustomPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
]