from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ValidationError
from .models import Product, ProductLike, ProductImage
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .forms import ProductForm
from django.views.generic import (
    View,
    DetailView,
    UpdateView,
    ListView,
    CreateView,
)
from django.utils.translation import gettext_lazy as _
from cart.models import CartItem
from decimal import Decimal
from django.db.models import Q


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        instance = context['product']
        category = instance.category.all().first()
        products = Product.objects.exclude(pk=instance.pk).by_order_amount(250, category=category)
        context['best_products'] = products
        return context


def _handle_product_form(request, product, images=None):
    if images is not None and len(images) > 4:
        raise ValidationError(_('Please select maximum 4 images for the product.'))

    queryset = ProductImage.objects.all().filter(product=product)
    if queryset.exists():
        for obj in queryset:
            obj.delete()

    for i in images:
        instance = ProductImage.objects.create(product=product, image=i)
        instance.save()


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def form_valid(self, form):
        valid = super(ProductCreateView, self).form_valid(form)
        images = self.request.FILES.getlist("images")

        if valid:
            _handle_product_form(self.request, form.instance, images=images)
            if self.request.user.is_staff:
                form.instance.is_approved = True
                form.instance.save()
            return valid


class ProductApprovePendingListView(LoginRequiredMixin, ListView):
    queryset = Product.objects.all().pending()
    paginate_by = 10
    context_object_name = 'products'
    template_name = 'product_pending_approve.html'

    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_staff:
            return super(ProductApprovePendingListView, self).get_context_data(**kwargs)
        else:
            raise Http404


class ProductApproveView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            info_message = _('You are not allowed for this action. Please sign in as ADMIN.')
        else:
            slug = self.kwargs.get("slug")
            instance = get_object_or_404(Product, slug=slug)
            instance.is_approved = True
            instance.save()
            info_message = _('Product has been approved successfully.')

        messages.add_message(request, messages.INFO, info_message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductRejectView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            info_message = _('Product has been approved successfully.')
        else:
            slug = self.kwargs.get("slug")
            instance = get_object_or_404(Product, slug=slug)
            instance.is_active = False
            instance.save()
            info_message = _('Product has been rejected successfully.')

        messages.add_message(request, messages.INFO, info_message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = "product_form.html"
    form_class = ProductForm

    def get_object(self):
        user = self.request.user
        slug = self.kwargs.get("slug")
        instance = get_object_or_404(Product, slug=slug)
        if user.type == 'distributor':
            if instance.is_active and not instance.is_deleted:
                return instance
            else:
                raise Http404
        elif user.is_staff:
            return instance
        else:
            raise Http404

    def form_valid(self, form):
        valid = super(ProductUpdateView, self).form_valid(form)
        images = self.request.FILES.getlist("images")
        if valid:
            _handle_product_form(self.request, form.instance, images=images)
        return valid


class ProductDeleteView(LoginRequiredMixin,View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            info_message = _('You are not allowed for this action. Please sign in as ADMIN.')
        else:
            slug = self.kwargs.get("slug")
            instance = get_object_or_404(Product, slug=slug)
            instance.is_active = False
            instance.save()
            info_message = _('Product has been deleted successfully.')

        messages.add_message(request, messages.INFO, info_message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductDeleteRequest(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        pk = self.request.POST.get("id")
        instance = get_object_or_404(Product, pk=pk)
        instance.is_deleted = True
        instance.save()
        info_message = _('Your delete request has been sent. We will inform you as soon as possible.')
        messages.add_message(self.request, messages.INFO, info_message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductDeletePendingListView(LoginRequiredMixin, ListView):
    queryset = Product.objects.all().deleted()
    paginate_by = 10
    context_object_name = 'products'
    template_name = 'product_pending_delete.html'

    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_staff:
            return super(ProductDeletePendingListView, self).get_context_data(**kwargs)
        else:
            raise Http404


def _update_item_qty_or_add(request, quantity, product=None):
    if product is not None and quantity < product.stock:
        cart = request.user.shopping_cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, is_active=True)
        if created:
            cart_item.quantity = quantity
            cart_item.save()
            return _('Product is added to your basket.')
        else:
            new_qty = cart_item.quantity + quantity
            if new_qty > product.stock:
                return _('Stock is not enough for quantity amount.')
            else:
                cart_item.quantity = new_qty
                cart_item.save()
                return _('Quantity amount is updated.')
    else:
        return _('Stock is not enough for quantity amount.')


class ProductAddToCartView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.type == 'customer':
            info_message = _('You need to sign in as a CUSTOMER to add items in your basket.')
            messages.add_message(self.request, messages.INFO, info_message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        pk = request.POST.get("id")
        qty = int(request.POST.get("quantity"))
        product = get_object_or_404(Product, pk=pk)

        if product.stock == 0:
            info_message = _('Product is out of stock.')
            messages.add_message(self.request, messages.INFO, info_message)
        else:
            info_message = _update_item_qty_or_add(request, qty, product=product)
            messages.add_message(self.request, messages.INFO, info_message)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductRemoveFromCartView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.type == 'customer':
            info_message = _('You need to sign in as a CUSTOMER to remove items from your basket')
            messages.add_message(self.request, messages.INFO, info_message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        pk = request.POST.get("id")
        product = get_object_or_404(Product, pk=pk)
        cart = request.user.shopping_cart
        cart_item = get_object_or_404(CartItem, product=product, cart=cart, is_active=True)
        cart_item.delete()

        info_message = _('Product is removed from your basket.')
        messages.add_message(self.request, messages.INFO, info_message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductRateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not request.user.type == 'customer':
            info_message = _('You need to sign in as a CUSTOMER to rate products')
            messages.add_message(self.request, messages.INFO, info_message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        pk = request.POST.get("id")
        rate = Decimal(request.POST.get("rating"))
        product = get_object_or_404(Product, pk=pk)
        product_like, created = ProductLike.objects.get_or_create(user=request.user, product=product)

        if rate > 10:
            rate = 10

        product_like.rate = rate
        product_like.save()

        info_message = _('Thank you for your vote.')
        messages.add_message(self.request, messages.INFO, info_message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductFilterView(View):

    def get(self, request):
        q = self.request.GET.get("q")
        qs = Product.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q) |
            Q(distributor__username__icontains=q)
        )

        context = {
            'q': q,
            'products': qs
        }

        return render(request, 'product_list.html', context)


