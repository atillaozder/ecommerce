from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Product(models.Model):

    # category = models.ManyToManyField('category.Category', blank=True)
    name = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    description = models.TextField(_('Description'), default='')
    price = models.DecimalField(_('Price'), default=0.00, max_digits=100, decimal_places=2)
    discount_price = models.DecimalField(_('Discount Price'), default=0.00, max_digits=100, decimal_places=2)
    order_amount = models.PositiveIntegerField(_('Total order'), default=0)
    # likes = models.ManyToManyField(User, through='ProductLike')
    stock = models.PositiveIntegerField(_('Stock'), default=0)
    discount = models.PositiveIntegerField(_('Discount'), default=0)

    is_approved = models.BooleanField(default=False, verbose_name='Approved')
    is_deleted = models.BooleanField(default=False, verbose_name='Deleted')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__ (self):
        return self.name

