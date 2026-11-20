import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import RegisterForm, CheckoutForm
from .models import Restaurant, Dish, Category, Order, OrderItem, Delivery


def cart_data(request):
    cart = request.session.get('cart', {})
    items, total, restaurant_id = [], Decimal('0'), None
    for dish_id, qty in cart.items():
        dish = Dish.objects.select_related('restaurant').filter(pk=dish_id, is_available=True).first()
        if not dish: continue
        restaurant_id = dish.restaurant_id
        line = dish.price * int(qty)
        total += line
        items.append({'id': dish.id, 'name': dish.name, 'qty': int(qty), 'price': str(dish.price), 'line': str(line)})
    return items, total, restaurant_id


def home(request):
    restaurants = Restaurant.objects.filter(is_active=True).order_by('-rating')[:6]
    categories = Category.objects.all()[:8]
    return render(request, 'delivery/home.html', {'restaurants': restaurants, 'categories': categories})


def catalog(request):
    qs = Restaurant.objects.filter(is_active=True).order_by('-rating')
    q = request.GET.get('q', '').strip()
    if q: qs = qs.filter(Q(name__icontains=q) | Q(cuisine__icontains=q) | Q(description__icontains=q))
    category = request.GET.get('category')
    if category:
        qs = qs.filter(dishes__category__slug=category).distinct()
    sort = request.GET.get('sort')
    if sort == 'rating': qs = qs.order_by('-rating')
    elif sort == 'price': qs = qs.order_by('minimum_order')
    page_obj = Paginator(qs, 20).get_page(request.GET.get('page'))
    return render(request, 'delivery/catalog.html', {'page_obj': page_obj, 'categories': Category.objects.all(), 'q': q, 'selected_category': category, 'sort': sort})


def restaurant_detail(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    dishes = restaurant.dishes.filter(is_available=True).select_related('category').order_by('category__name', 'name')
    categories = Category.objects.filter(dishes__restaurant=restaurant).distinct()
    return render(request, 'delivery/restaurant.html', {'restaurant': restaurant, 'dishes': dishes, 'categories': categories})


def about(request):
    return render(request, 'delivery/about.html')


def search(request):
    q = request.GET.get('q', '').strip()
    dishes = Dish.objects.filter(is_available=True).select_related('restaurant', 'category')
    if q: dishes = dishes.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(restaurant__name__icontains=q))
    page_obj = Paginator(dishes.order_by('name'), 20).get_page(request.GET.get('page'))
    return render(request, 'delivery/search.html', {'page_obj': page_obj, 'q': q})


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Аккаунт создан. Добро пожаловать!')
        return redirect('profile')
    return render(request, 'delivery/form.html', {'form': form, 'page_title': 'Регистрация', 'button': 'Создать аккаунт'})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).select_related('restaurant').order_by('-created_at')
    return render(request, 'delivery/profile.html', {'orders': orders})


def cart_page(request):
    items, total, restaurant_id = cart_data(request)
    restaurant = Restaurant.objects.filter(pk=restaurant_id).first() if restaurant_id else None
    return render(request, 'delivery/cart.html', {'items': items, 'total': total, 'restaurant': restaurant, 'form': CheckoutForm()})


def cart_api(request):
    if request.method != 'POST': return JsonResponse({'error': 'POST required'}, status=405)
    try: data = json.loads(request.body or '{}')
    except json.JSONDecodeError: return JsonResponse({'error': 'Некорректный запрос'}, status=400)
    dish = get_object_or_404(Dish.objects.select_related('restaurant'), pk=data.get('dish_id'), is_available=True)
    cart = request.session.get('cart', {})
    current_restaurant = None
    if cart:
        first = Dish.objects.filter(pk=next(iter(cart))).first()
        current_restaurant = first.restaurant_id if first else None
    if current_restaurant and current_restaurant != dish.restaurant_id:
        return JsonResponse({'error': 'В корзине могут быть блюда только одного ресторана. Очистите корзину, чтобы выбрать другой.'}, status=400)
    cart[str(dish.id)] = min(int(cart.get(str(dish.id), 0)) + 1, 30)
    request.session['cart'] = cart
    count = sum(int(x) for x in cart.values())
    return JsonResponse({'ok': True, 'count': count, 'message': f'{dish.name} добавлено в корзину'})


def cart_remove(request, dish_id):
    cart = request.session.get('cart', {})
    cart.pop(str(dish_id), None)
    request.session['cart'] = cart
    return redirect('cart')

@login_required
def checkout(request):
    items, subtotal, restaurant_id = cart_data(request)
    if not items:
        messages.error(request, 'Корзина пуста.')
        return redirect('catalog')
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    form = CheckoutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        zone = form.cleaned_data['zone']
        if subtotal < restaurant.minimum_order:
            form.add_error(None, f'Минимальный заказ этого ресторана — {restaurant.minimum_order} ₽.')
        elif zone.pk != restaurant.delivery_zone_id:
            form.add_error('zone', 'Ресторан пока доставляет только в указанную на странице ресторана зону.')
        else:
            prep = 0
            for row in items:
                dish = Dish.objects.get(pk=row['id'])
                prep = max(prep, dish.cooking_minutes)
            order = Order.objects.create(user=request.user, restaurant=restaurant, zone=zone,
                address=form.cleaned_data['address'], delivery_price=zone.delivery_price,
                total=subtotal + zone.delivery_price, preparation_minutes=prep)
            for row in items:
                dish = Dish.objects.get(pk=row['id'])
                OrderItem.objects.create(order=order, dish=dish, quantity=row['qty'], price=dish.price)
            Delivery.objects.create(order=order)
            request.session['cart'] = {}
            messages.success(request, f'Заказ №{order.pk} оформлен!')
            return redirect('profile')
    return render(request, 'delivery/checkout.html', {'form': form, 'items': items, 'subtotal': subtotal, 'restaurant': restaurant})
