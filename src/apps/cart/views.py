from django.shortcuts import render, redirect
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Cart, CartItem
from apps.product.models import Product
from apps.order.models import Order


class CartView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.is_staff or not request.user.user_type == 'customer':
            raise Http404
        instance = request.user.shopping_cart
        return render(request, 'shopping_cart.html', {'cart': instance})


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.is_staff or not request.user.user_type == 'customer':
            raise Http404

        cart = request.user.shopping_cart
        addresses = request.user.addresses.all()
        shipping_address = request.user.shipping_address
        billing_address = request.user.billing_address
        context = {
            'cart': cart,
            'addresses': addresses,
            'shipping': shipping_address,
            'billing': billing_address,
        }
        return render(request, 'checkout.html', context)