from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )

    field_order = [
        'name',
        'category',
        'description',
        'price',
        'discount',
        'stock',
        'images',
    ]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Name'),
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Description'),
        })
        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Price'),
        })
        self.fields['discount'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Discount'),
        })
        self.fields['stock'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Stock'),
        })

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'description',
            'price',
            'discount',
            'stock',
            'images'
        ]

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError('Price must be higher than 0.')
        return price

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock <= 0:
            raise forms.ValidationError('Stock must be higher than 0.')
        return stock

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        if commit:
            instance.is_approved = False
            instance.save()
        return instance
