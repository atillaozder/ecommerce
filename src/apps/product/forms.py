from django import forms
from django.utils.translation import gettext_lazy as _

from product.models import Product, ProductImage
from brand.models import Brand

class ProductForm(forms.ModelForm):
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )

    field_order = [
        'name',
        'category',
        'essential_product',
        'brand',
        'description',
        'price',
        'discount',
        'stock',
        'weight',
        'images',
    ]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Name'),
        })
        self.fields['category'].widget.attrs.update({
            'class' : 'form-control',
        })
        self.fields['essential_product'].widget.attrs.update({
            'class' : 'form-control',
        })
        self.fields['brand'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Brand'),
        })
        self.fields['description'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Description'),
        })
        self.fields['price'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Price'),
        })
        self.fields['discount'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Discount'),
        })
        self.fields['stock'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Stock'),
        })
        self.fields['weight'].widget.attrs.update({
            'class' : 'form-control',
            'placeholder': _('Weight'),
        })

    class Meta:
        model = Product
        fields = [
            'category',
            'essential_product',
            'name',
            'description',
            'price',
            'discount',
            'stock',
            'weight',
            'brand',
            'images'
        ]
