from django.db import models
from django.utils.translation import gettext_lazy as _


class Address(models.Model):

    # country =
    city = models.CharField(_('City'), max_length=255)
    address_line = models.TextField(_('Address'), blank=False)
    notes = models.TextField(_('Notes'), blank=True)
    postal_code = models.CharField(_('Postal Code'), blank=True, max_length=6)
    slug = models.SlugField(unique=True, blank=True, max_length=255)

    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__ (self):
        return self.name

