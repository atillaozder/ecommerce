from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import *

app_name = 'users'

registration_patterns = [
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register', UserRegisterView.as_view(), name='register'),
    path('password/change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/<uidb64>/<token>', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm')
]

urlpatterns = [
    path('', include(registration_patterns)),
    path('account/delete', UserDeleteView.as_view(), name='delete'),
    path('account/image/change', UserImageUpdateView.as_view(), name='update_image'),
    path('account/edit', UserUpdateView.as_view(), name='update'),
    path('account/<username>', UserDetailView.as_view(), name='profile'),
    path('distributors/pending', DistributorPendingListView.as_view(), name='distributors'),
    path('account/<username>/approve', DistributorApproveView.as_view(), name='approve'),
    path('account/<username>/reject', DistributorRejectView.as_view(), name='reject'),
]
