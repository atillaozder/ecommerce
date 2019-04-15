from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Address


class AddressForm(forms.ModelForm):
    field_order = ['country', 'city', 'address_line', 'postal_code', 'notes']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['country'].widget.attrs.update({
            'placeholder': _('Country'),
            'class': 'form-control',
        })
        self.fields['city'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('City'),
        })
        self.fields['address_line'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Address Information'),
        })
        self.fields['postal_code'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Postal Code'),
            'pattern': '[0-9]+'
        })
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Additional Notes'),
        })

    class Meta:
        model = Address
        fields = [
            'country',
            'city',
            'address_line',
            'notes',
            'postal_code'
        ]

    def save(self, commit=True):
        address = super(AddressForm, self).save(commit=False)
        if commit:
            address.save()
        return address
