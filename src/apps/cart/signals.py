from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from cart.models import CartItem, Cart

""" Recalculate Cart Item object item's total price after quantity has changed """


@receiver(pre_save, sender=CartItem)
def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    instance.update_item_total_price()


"""
Recalculate Cart subtotal price after Cart Item object has changed or
either Cart Item object has deleted or Product object has deleted 
"""


@receiver([post_save, post_delete], sender=CartItem)
def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
    if instance.cart is not None:
        instance.cart.update_subtotal()


""" Recalculate Cart total price before Cart is saved """


@receiver(pre_save, sender=Cart)
def cart_pre_save_receiver(sender, instance, *args, **kwargs):
    instance.update_total_with_tax()
