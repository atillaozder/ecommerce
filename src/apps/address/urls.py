from django.urls import path

from .views import (
    AddressCreateView,
    AddressDeleteView,
    AddressUpdateView,
)

app_name = 'address'



urlpatterns = [
    path('create', AddressCreateView.as_view(), name='create'),
    path('update/<pk>', AddressUpdateView.as_view(), name='update'),
    path('delete', AddressDeleteView.as_view(), name='delete'),
]