from django.urls import path
from .views import *

app_name = 'address'

urlpatterns = [
    path('create', AddressView.as_view(), name='create'),
    path('update/<pk>', AddressView.as_view(), name='update'),
    path('delete', AddressView.as_view(), name='delete'),
]