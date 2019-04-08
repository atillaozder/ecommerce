from django.contrib import admin
from .models import Product, ProductLike, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_approved', 'is_active', 'is_deleted')
    list_editable = ('is_approved', 'is_active', 'is_deleted')
    list_filter = ('is_active', 'is_approved', 'is_deleted')


@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rate')


admin.site.register(ProductImage)