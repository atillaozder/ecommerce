from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.urls import reverse
from django.db.models.signals import pre_save
from utils.utils import random_string_generator
import string

User = get_user_model()

class OrderQuerySet(models.query.QuerySet):
    def recent(self):
        return self.order_by("-updated", "-timestamp")

    def not_refunded(self):
        return self.exclude(status='refunded')

    def not_shipped(self):
        return self.exclude(status='shipped')

    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(updated__gte=start_date)
        return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

class Order(models.Model):
    CREATED 	= _('created')
    PAID 		= _('paid')
    SHIPPED 	= _('shipped')
    REFUNDED	= _('refunded')

    ORDER_STATUS_CHOICES = (
        (CREATED, _('Created')),
        (PAID, _('Paid')),
        (SHIPPED, _('Shipped')),
        (REFUNDED, _('Refunded')),
    )

    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)

    shipping_address = models.ForeignKey('address.Address',
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         related_name='+')

    billing_address = models.ForeignKey('address.Address',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        related_name='+')

    # cart_items = models.ManyToManyField('cart.CartItem')

    status = models.CharField(_('Status'),
                              max_length=120,
                              default=CREATED,
                              choices=ORDER_STATUS_CHOICES)

    order_id = models.CharField(_('Order ID'),
                                max_length=6,
                                null=True,
                                blank=True,
                                editable=False)

    total = models.DecimalField(_('Total'),
                                default=0.00,
                                max_digits=100,
                                decimal_places=2
                                )

    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-timestamp', '-updated']

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})

    def _order_id_generator(self, new_order_id=None):
        if new_order_id is not None:
            randstr = new_order_id
        else:
            randstr = random_string_generator(size=6, chars=string.ascii_uppercase + string.digits)

        qs_exists = Order.objects.filter(order_id=randstr).exists()
        if qs_exists:
            return self.order_id_generator(self, new_order_id=new_order_id)
        self.order_id = randstr

@receiver(pre_save, sender=Order)
def order_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance._order_id_generator()
