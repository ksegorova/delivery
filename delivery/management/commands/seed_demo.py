from django.core.management.base import BaseCommand
from delivery.models import DeliveryZone, Category, Restaurant, Dish

class Command(BaseCommand):
    help = 'Создаёт демонстрационные рестораны и блюда для локального проекта'
    def handle(self, *args, **kwargs):
        zone, _ = DeliveryZone.objects.get_or_create(name='Центральная зона', defaults={'delivery_price': 149, 'description':'Доставка в пределах центрального района'})
        cats = {}
        for name, slug in [('Пицца','pizza'),('Бургеры','burgers'),('Суши','sushi'),('Горячее','hot'),('Десерты','desserts')]:
            cats[slug], _ = Category.objects.get_or_create(slug=slug, defaults={'name':name})
        data = [
            ('Тесто & Сыр','pizza-house','Пицца и паста из печи','Итальянская',550,4.9,35,[('Маргарита','Томатный соус, моцарелла и базилик',590,'Пицца 30 см',18,'pizza'),('Пепперони','Пикантная колбаса и сыр',690,'Пицца 30 см',22,'pizza'),('Тирамису','Классический десерт с кофе',320,'120 г',12,'desserts')]),
            ('Бургерная №1','burger-one','Сочные бургеры и картофель фри','Американская',450,4.8,30,[('Чизбургер','Говяжья котлета, чеддер и соус',490,'280 г',15,'burgers'),('Двойной бургер','Две котлеты, сыр и овощи',690,'390 г',24,'burgers'),('Картофель фри','Хрустящий картофель',190,'150 г',10,'hot')]),
            ('Рис и Рыба','rice-fish','Роллы и азиатская кухня','Японская',700,4.7,45,[('Филадельфия','Лосось, сливочный сыр и огурец',620,'8 шт.',20,'sushi'),('Калифорния','Краб, авокадо и икра тобико',540,'8 шт.',18,'sushi'),('Том ям','Острый суп с морепродуктами',590,'350 мл',25,'hot')]),
            ('Домашний обед','home-lunch','Понятная домашняя еда каждый день','Домашняя',400,4.6,40,[('Куриная котлета','С картофельным пюре',390,'320 г',17,'hot'),('Паста с грибами','Сливочный соус и шампиньоны',420,'300 г',19,'hot'),('Сырники','Со сметаной',290,'180 г',14,'desserts')]),
        ]
        for name, slug, desc, cuisine, minimum, rating, eta, dishes in data:
            r, _ = Restaurant.objects.get_or_create(slug=slug, defaults={'name':name,'description':desc,'cuisine':cuisine,'delivery_zone':zone,'minimum_order':minimum,'rating':rating,'delivery_minutes':eta})
            for dn, dd, price, weight, mins, cat in dishes:
                Dish.objects.get_or_create(restaurant=r, name=dn, defaults={'description':dd,'price':price,'weight':weight,'cooking_minutes':mins,'category':cats[cat]})
        self.stdout.write(self.style.SUCCESS('Демо-каталог создан. Добавлено 4 ресторана и блюда.'))
