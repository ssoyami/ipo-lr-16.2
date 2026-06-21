from django.contrib import admin
from .models import (
    Category,
    Manufacturer,
    Product,
    Cart,
    CartItem,
)
from .models import Order, OrderItem

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)