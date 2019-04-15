from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from .models import Product
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ValidationError
from .models import Product, ProductLike, ProductImage
from django.contrib import messages
from django.shortcuts import render,get_object_or_404
from .forms import ProductForm
from django.views.generic import (
    View,
    DetailView,
    UpdateView,
    ListView,
    CreateView,
)
from django.utils.translation import gettext_lazy as _

# Create your views here.


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
        if user.user_type == 'distributor':
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

