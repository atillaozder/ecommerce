from django.shortcuts import render, redirect
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import CartItem
from order.models import Order


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


class CheckoutDoneView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if request.user.is_staff or not request.user.user_type == 'customer':
            raise Http404

        user = request.user
        billing = user.billing_address
        shipping = user.shipping_address
        if billing is not None and shipping is not None:
            cart = user.shopping_cart
            cart_items = cart.cartitem_set.all()
            order = Order.objects.create(
                user=user,
                billing_address=billing,
                shipping_address=shipping,
                total=cart.total
            )

            for item in cart_items:
                product = item.product
                if item.quantity > product.stock:
                    item.quantity = product.stock
                    item.save()

                product.stock -= item.quantity
                product.order_amount += item.quantity
                product.save()
                order.cart_items.add(item)

            order.save()
            for product in cart.products.all():
                items = CartItem.objects.all().filter(product=product, cart=cart)
                for item in items:
                    item.cart = None
                    item.save()

            info_message = _('Your order is placed.')
            messages.add_message(request, messages.INFO, info_message)
            return redirect('orders:list')

        info_message = _('You need to set a default billing and shipping addresses.')
        messages.add_message(request, messages.INFO, info_message)
        return redirect('carts:checkout')

