from django.contrib import admin

from django.contrib import admin
from order.models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('user', 'order_id', 'timestamp', 'updated', 'status')
    list_filter   = ('status',)
