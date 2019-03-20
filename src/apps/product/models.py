from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q
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

    User = get_user_model()

    class ProductQuerySet(models.query.QuerySet):
        def active(self):
            return self.filter(is_active=True)

        def not_active(self):
            return self.filter(is_active=False)

        def deleted(self):
            return self.filter(is_deleted=True)

        def not_deleted(self):
            return self.filter(is_deleted=False)

        def approved(self):
            return self.filter(is_approved=True)

        def not_approved(self):
            return self.filter(is_approved=False)

        def accepted(self):
            return self.active().not_deleted().approved()

        def pending(self):
            return self.active().not_deleted().not_approved()

        def featured(self):
            qs_orders = self.by_order_amount(100)
            qs_likes = self.by_likes(10)
            qs_discounts = self.accepted().filter(discount__gte=20)
            return (qs_orders | qs_likes | qs_discounts).distinct()

        def by_order_amount(self, amount, category=None):
            if category is None:
                return self.accepted().filter(order_amount__gte=amount)
            return self.accepted().filter(category_name=category.name).filter(order_amount_gte=amount)

        def by_likes(self, like_amount):
            return self.accepted().annotate(num_like=('likes')).filter(num_like__gte=like_amount)

        def recent(self):
            return self.accepted().order_by("-updated", "-timestamp")

        def by_range(self, start_date, end_date=None):
            if end_date is None:
                return self.filter(updated__gte=start_date)
            return self.filter(updated_gte=start_date).filter(updated_lte=end_date)

    class ProductManager(models.Manager):
        def get_queryset(self):
            return ProductQuerySet(self.model, using=self._db)