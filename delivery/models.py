from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

class DeliveryZone(models.Model):
    name = models.CharField('Название зоны', max_length=80)
    delivery_price = models.DecimalField('Стоимость доставки', max_digits=7, decimal_places=2, default=149)
    description = models.CharField('Описание', max_length=180, blank=True)
    def __str__(self): return self.name

class Category(models.Model):
    name = models.CharField('Название', max_length=80)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name

class Restaurant(models.Model):
    name = models.CharField('Название', max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание')
    cuisine = models.CharField('Кухня', max_length=80)
    image = models.ImageField('Изображение', upload_to='restaurants/', blank=True)
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.PROTECT, verbose_name='Зона доставки')
    minimum_order = models.DecimalField('Минимальный заказ', max_digits=8, decimal_places=2, default=500)
    rating = models.FloatField('Рейтинг', default=4.7, validators=[MinValueValidator(0)])
    delivery_minutes = models.PositiveIntegerField('Ориентир доставки', default=40)
    is_active = models.BooleanField('Активен', default=True)
    def __str__(self): return self.name

class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='dishes')
    name = models.CharField('Название', max_length=120)
    description = models.CharField('Описание', max_length=240)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    weight = models.CharField('Вес', max_length=40, blank=True)
    cooking_minutes = models.PositiveIntegerField('Время приготовления', default=15)
    image = models.ImageField('Изображение', upload_to='dishes/', blank=True)
    is_available = models.BooleanField('В наличии', default=True)
    def __str__(self): return f'{self.name} — {self.restaurant.name}'

class Order(models.Model):
    STATUS = [('new','Новый'),('cooking','Готовится'),('ready','Готов'),('delivering','В пути'),('done','Доставлен')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='food_orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    zone = models.ForeignKey(DeliveryZone, on_delete=models.PROTECT)
    address = models.CharField('Адрес доставки', max_length=250)
    status = models.CharField('Статус', max_length=20, choices=STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_price = models.DecimalField(max_digits=7, decimal_places=2)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    preparation_minutes = models.PositiveIntegerField(default=0)
    def __str__(self): return f'Заказ №{self.pk}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    def __str__(self): return f'{self.dish.name} × {self.quantity}'

class Courier(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    def __str__(self): return self.name

class Delivery(models.Model):
    STATUS = [('waiting','Ожидает курьера'),('delivering','Доставляется'),('delivered','Доставлен')]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='waiting')
    updated_at = models.DateTimeField(auto_now=True)
