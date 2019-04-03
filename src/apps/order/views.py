from django.shortcuts import render

from django.shortcuts import render, Http404, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from .models import Order

class OrderListView(LoginRequiredMixin, ListView):
    paginate_by = 10
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get(self, request, *args, **kwargs):
        if not request.user.type == 'customer' or request.user.is_staff:
            raise Http404
        return super(OrderListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.all().recent().filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    def get_object(self):
        order_id = self.kwargs.get("order_id")
        instance = get_object_or_404(Order, order_id=order_id)
        return instance

    def get_context_data(self, *args, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        instance = context['order']
        list = []
        for cart_item in instance.cart_items.all():
            list.append(cart_item.product)

        context['products'] = list
        return context
