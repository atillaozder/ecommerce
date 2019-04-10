from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

User = get_user_model()


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    item_total = models.DecimalField(_('Total Price'), default=0.00, max_digits=100, decimal_places=2)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ['cart', 'product']

    def __str__(self):
        return self.product.__str__()

    def update_item_total_price(self):
        qts = self.quantity
        price = self.product.get_price()
        total = Decimal(qts) * price

        active = self.product.is_active
        approved = self.product.is_approved
        stock = self.product.stock
        self.is_active = active
        if active and approved and stock > 0:
            self.item_total = total
        else:
            self.item_total = 0


class Cart(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='shopping_cart')

    products = models.ManyToManyField('product.Product',
                                      through='CartItem')

    total = models.DecimalField(_('Total'),
                                default=0.00,
                                max_digits=100,
                                decimal_places=2)

    subtotal = models.DecimalField(_('Subtotal'),
                                   default=0.00,
                                   max_digits=100,
                                   decimal_places=2)

    timestamp = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __str__(self):
        return self.user.username

    def get_total_tax(self):
        return self.total - self.subtotal

    def get_total_discount(self):
        discount = 0
        for p in self.products.all():
            discount += (p.price - p.discount_price)
        return Decimal(discount)

    def update_total_with_tax(self):
        if self.subtotal > 0:
            self.total = Decimal(self.subtotal) * Decimal(1.08)
        else:
            self.total = 0.00

    def get_total_with_discount(self):
        discount = self.get_total_discount()
        return self.total - discount

    def update_subtotal(self):
        total = 0
        cart_items = self.cartitem_set.all()
        for item in cart_items:
            total += item.item_total

        if self.subtotal != total:
            self.subtotal = total
            self.save()
