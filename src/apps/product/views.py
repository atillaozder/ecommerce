from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy

from .models import Product
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ValidationError
from .models import Product, ProductLike, ProductImage
from django.contrib import messages
from django.shortcuts import render
from .forms import ProductForm
from django.views.generic import (
    View,
    DetailView,
    UpdateView,
    ListView,
    CreateView,
)

# Create your views here.

class ProductDetailView(DetailView) :
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView,self).get_context_data(**kwargs)
        instance = context ['product']
        category = instance.category.all().first()
        products = Product.objects.exclude(pk=instance.pk).by_order_amount(250, category=category)
        context['best_products'] = products
        return context


def _handle_product_form(request, product, images=None):
    if images is not None and len(images) > 4:
        raise ValidationError(_('Please select maximum 4 images for the product.'))

    if product.brand:
        user = request.user
        qs_exists = user.distributor.brands.all().filter(pk=product.brand.pk).exists()
        if not qs_exists and not user.is_staff:
            raise ValidationError(_('Please select a brand that you distribute: %(value)s'),
                                code='invalid',
                                params={'value': product.brand},)

    queryset = ProductImage.objects.all().filter(product=product)
    if queryset.exists():
        for obj in queryset:
            obj.delete()

    for i in images:
        instance = ProductImage.objects.create(product=product, image=i)
        instance.save()


class ProductCreateView (LoginRequiredMixin,CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def form_valid(self, form):
        valid = super(ProductCreateView,self).form_valid(form)
        images =self.request.FILES.getlist("images")

        if valid :
            _handle_product_form(self.request, form.instance,images = images)
            if self.request.user.is_staff:
                form.instance.is_approved = True
                form.instanceSave()
            return valid
