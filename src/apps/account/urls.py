from django.urls import path, include
from django.contrib.auth.views import (LogoutView)
from .views import *

app_name = 'users'

registration_patterns = [
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('password/change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/<uidb64>/<token>', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm')
]

urlpatterns = [
    path('', include(registration_patterns)),
]
