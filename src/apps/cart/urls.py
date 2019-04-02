from django.urls import path
from .views import *

app_name = 'carts'

urlpatterns = [
    path('', CartView.as_view(), name='detail'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('checkout/done', CheckoutDoneView.as_view(), name='checkout_done'),
]
