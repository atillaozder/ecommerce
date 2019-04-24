from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from utils.utils import unique_slug_generator
from .models import Product


@receiver(pre_save, sender=Product)
def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
    instance.update_discount_price()


# Recalculate Cart Item item total price after product has updated
@receiver(post_save, sender=Product)
def product_post_save_receiver(sender, instance, *args, **kwargs):
    instance.update_cart_item()

# # Recalculate Cart subtotal price before product is deleted
# @receiver(pre_delete, sender=Product)
# def product_pre_delete_receiver(sender, instance, *args, **kwargs):
#     if instance.price > 0 and instance.is_approved and instance.is_active:
#         product = Product.objects.get(pk=instance.id)
#         carts = Cart.objects.all().filter(products__id=instance.id)
#         for cart in carts:
#             cart.products.remove(product)
#             cart.update_subtotal()
