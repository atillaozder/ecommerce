from django.db import models
import datetime
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils.utils import get_upload_path
from cart.models import CartItem
from decimal import Decimal
from django.db.models import Count, Q
from django.conf import settings

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
            return self.accepted()\
                .annotate(order=Count('order_amount'))\
                .filter(order__gt=amount)
        return self.accepted()\
            .filter(category__name=category.name)\
            .annotate(order=Count('order_amount'))\
            .filter(order__gt=amount)

    def by_likes(self, like_amount):
        return self.accepted()\
            .annotate(num_like=Count('likes'))\
            .filter(num_like__gte=like_amount)

    def recent(self):
        return self.accepted().order_by("-updated", "-timestamp")

    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(updated__gte=start_date)
        return self.filter(updated__gte=start_date).filter(updated__lte=end_date)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)


class Product(models.Model):
    distributor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.ManyToManyField('category.Category', blank=True)
    name = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    description = models.TextField(_('Description'), default='')
    price = models.DecimalField(_('Price'), default=0.00, max_digits=100, decimal_places=2)
    discount_price = models.DecimalField(_('Discount Price'), default=0.00, max_digits=100, decimal_places=2)
    order_amount = models.PositiveIntegerField(_('Total order'), default=0)
    likes = models.ManyToManyField(User, through='ProductLike', related_name='likes')
    stock = models.PositiveIntegerField(_('Stock'), default=0)
    discount = models.PositiveIntegerField(_('Discount'), default=0)

    is_approved = models.BooleanField(default=False, verbose_name='Approved')
    is_deleted = models.BooleanField(default=False, verbose_name='Deleted')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    def get_price(self):
        return Decimal(self.price)

    def get_absolute_price(self):
        if self.discount > 0:
            return Decimal(self.discount_price)
        return Decimal(self.price)

    def get_saved_price(self):
        if self.discount > 0:
            return Decimal(self.price) - Decimal(self.discount_price)

    def get_first_image_url(self):
        url = settings.STATIC_URL + 'ecommerce/img/defaults/no_image.jpg'
        if self.product_image.exists():
            url = self.product_image.first().image.url
        return url

    def is_todays_product(self):
        start_date = timezone.now().date() - datetime.timedelta(hours=24)
        qs_exist = Product.objects.all().filter(pk=self.pk).by_range(start_date).exists()
        return qs_exist

    def get_avg_like(self):
        like_count = self.likes.all().count()
        if like_count > 0:
            rate = 0
            for product in self.product_like.all():
                rate += product.rate
            avg = Decimal(rate / like_count)
            return avg
        return 0

    def update_cart_item(self):
        items = CartItem.objects.all().filter(product=self)
        for item in items:
            item.save()

    def update_discount_price(self):
        if self.discount > 0:
            total_price = self.get_price()
            discount_amount = total_price * Decimal(self.discount) / 100
            new_price = total_price - discount_amount
            self.discount_price = new_price
        else:
            self.discount_price = self.price


class ProductImage(models.Model):
    product = models.ForeignKey('Product',
                                on_delete=models.CASCADE,
                                related_name='product_image')

    image = models.ImageField(upload_to=get_upload_path,
                              height_field='height_field',
                              width_field='width_field',
                              null=True,
                              blank=True,
                              verbose_name='Product Image',
                              max_length=255)

    width_field = models.PositiveIntegerField(default=0,
                                              verbose_name='Image Width',
                                              null=True,
                                              blank=True)

    height_field = models.PositiveIntegerField(default=0,
                                               verbose_name='Image Height',
                                               null=True,
                                               blank=True)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')


class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='product_like')

    rate = models.DecimalField(default=0, max_digits=3, decimal_places=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Product Like')
        verbose_name_plural = _('Product Likes')
        unique_together = ['user', 'product']

    def _str_(self):
        return "{user} - {product}".format(user=self.user.username, product=self.product.name)