from django.contrib import admin
from .models import DeliveryZone, Category, Restaurant, Dish, Order, OrderItem, Courier, Delivery
admin.site.register([DeliveryZone, Category, Restaurant, Dish, Order, OrderItem, Courier, Delivery])
