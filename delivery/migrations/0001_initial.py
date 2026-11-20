from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Category', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('name', models.CharField(max_length=80, verbose_name='Название')), 
            ('slug', models.SlugField(unique=True))
            ]),
        migrations.CreateModel(name='Courier', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('name', models.CharField(max_length=120)), 
            ('phone', models.CharField(blank=True, max_length=30))
            ]),
        migrations.CreateModel(name='DeliveryZone', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('name', models.CharField(max_length=80, verbose_name='Название зоны')), 
            ('delivery_price', models.DecimalField(decimal_places=2, default=149, max_digits=7, verbose_name='Стоимость доставки')), 
            ('description', models.CharField(blank=True, max_length=180, verbose_name='Описание'))
            ]),
        migrations.CreateModel(name='Restaurant', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('name', models.CharField(max_length=120, verbose_name='Название')), 
            ('slug', models.SlugField(unique=True)), 
            ('description', models.TextField(verbose_name='Описание')), 
            ('cuisine', models.CharField(max_length=80, verbose_name='Кухня')), 
            ('image', models.ImageField(blank=True, upload_to='restaurants/', verbose_name='Изображение')), 
            ('minimum_order', models.DecimalField(decimal_places=2, default=500, max_digits=8, verbose_name='Минимальный заказ')), 
            ('rating', models.FloatField(default=4.7, verbose_name='Рейтинг')), 
            ('delivery_minutes', models.PositiveIntegerField(default=40, verbose_name='Ориентир доставки')), 
            ('is_active', models.BooleanField(default=True, verbose_name='Активен')), 
            ('delivery_zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='delivery.deliveryzone', verbose_name='Зона доставки'))
            ]),
        migrations.CreateModel(name='Dish', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('name', models.CharField(max_length=120, verbose_name='Название')), 
            ('description', models.CharField(max_length=240, verbose_name='Описание')), 
            ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Цена')), 
            ('weight', models.CharField(blank=True, max_length=40, verbose_name='Вес')), 
            ('cooking_minutes', models.PositiveIntegerField(default=15, verbose_name='Время приготовления')), 
            ('image', models.ImageField(blank=True, upload_to='dishes/', verbose_name='Изображение')), 
            ('is_available', models.BooleanField(default=True, verbose_name='В наличии')), 
            ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dishes', to='delivery.category')), 
            ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dishes', to='delivery.restaurant'))
            ]),
        migrations.CreateModel(name='Order', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('address', models.CharField(max_length=250, verbose_name='Адрес доставки')), 
            ('status', models.CharField(choices=[('new','Новый'),('cooking','Готовится'),('ready','Готов'),('delivering','В пути'),('done','Доставлен')], default='new', max_length=20, verbose_name='Статус')), 
            ('created_at', models.DateTimeField(auto_now_add=True)), 
            ('delivery_price', models.DecimalField(decimal_places=2, max_digits=7)), 
            ('total', models.DecimalField(decimal_places=2, default=0, max_digits=9)), 
            ('preparation_minutes', models.PositiveIntegerField(default=0)), 
            ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='delivery.restaurant')), 
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_orders', to=settings.AUTH_USER_MODEL)), 
            ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='delivery.deliveryzone'))
            ]),
        migrations.CreateModel(name='OrderItem', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('quantity', models.PositiveIntegerField(default=1)), 
            ('price', models.DecimalField(decimal_places=2, max_digits=8)), 
            ('dish', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='delivery.dish')), 
            ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='delivery.order'))
            ]),
        migrations.CreateModel(name='Delivery', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), 
            ('status', models.CharField(choices=[('waiting','Ожидает курьера'),('delivering','Доставляется'),('delivered','Доставлен')], default='waiting', max_length=20)), 
            ('updated_at', models.DateTimeField(auto_now=True)), 
            ('courier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='delivery.courier')), 
            ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery', to='delivery.order'))
            ]),
    ]
