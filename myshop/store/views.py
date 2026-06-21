from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from openpyxl import Workbook
import os
from .models import (
    Product,
    Category,
    Manufacturer,
    Cart,
    CartItem,
    Order,
    OrderItem
)
from rest_framework import viewsets
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ManufacturerSerializer,
    CartSerializer,
    CartItemSerializer
)
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def about_author(request):
    return HttpResponse("Эта страница об авторе. Автор Санкевич Яна Александрона.")

def about_shop(request):
    return HttpResponse("Это страница о магазине. Это магазин масок и костюмов для праздников. (:")

def main_page(request):
    products = Product.objects.order_by('-id')[:4]
    categories = Category.objects.all()

    return render(
        request,
        'store/index.html',
        {
            'products': products,
            'categories': categories
        }
    )


def product_list(request):
    products = Product.objects.all()

    category = request.GET.get('category')
    manufacturer = request.GET.get('manufacturer')
    country = request.GET.get('country')
    search = request.GET.get('search')

    if category:
        products = products.filter(
            categories__id=category
        ).distinct()

    if manufacturer:
        products = products.filter(
            manufacturer__id=manufacturer
        )

    if country:
        products = products.filter(
            manufacturer__country__icontains=country
        )

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    return render(
        request,
        'store/product_list.html',
        {
            'products': products,
            'categories': Category.objects.all(),
            'manufacturers': Manufacturer.objects.all(),
        }
    )

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(
        request,
        'store/product_detail.html',
        {'product': product}
    )


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect('cart')


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= item.product.stock_quantity:
            item.quantity = quantity
            item.save()

    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    return redirect('cart')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.items.all()

    total_price = sum(
        item.item_price()
        for item in items
    )

    return render(
        request,
        'store/cart.html',
        {
            'cart': cart,
            'items': items,
            'total_price': total_price
        }
    )
@login_required
def checkout(request):

    if request.method == 'POST':

        country = request.POST.get('country')
        city = request.POST.get('city')
        street = request.POST.get('street')
        house = request.POST.get('house')
        entrance = request.POST.get('entrance')
        floor = request.POST.get('floor')
        apartment = request.POST.get('apartment')

        address = (
        f"{country}, "
        f"г. {city}, "
        f"ул. {street}, "
        f"д. {house}, "
        f"подъезд {entrance}, "
        f"этаж {floor}, "
        f"кв. {apartment}"
        )


        request.session['delivery_address'] = address

        cart = Cart.objects.get(user=request.user)

        for item in cart.items.all():

            product = item.product

        if product.stock_quantity >= item.quantity:

            product.stock_quantity -= item.quantity
            product.save()

        cart.items.all().delete()

        return render(
            request,
            'store/order_success.html',
            {'address': address}
        )

    return render(request, 'store/checkout.html')

@login_required
def download_receipt(request):
    cart = Cart.objects.get(user=request.user)

    address = request.session.get(
        'delivery_address',
        'Не указан'
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Чек"

    ws.append(["ЧЕК"])
    ws.append([])
    ws.append(["Покупатель", request.user.username])
    ws.append(["Адрес доставки", address])
    ws.append([])

    ws.append([
        "Товар",
        "Количество",
        "Цена",
        "Сумма"
    ])

    total = 0

    for item in cart.items.all():
        subtotal = item.product.price * item.quantity

        total += subtotal

        ws.append([
            item.product.name,
            item.quantity,
            float(item.product.price),
            float(subtotal)
        ])

    ws.append([])
    ws.append(["ИТОГО", "", "", float(total)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename="receipt.xlsx"'
    )

    wb.save(response)

    order = Order.objects.create(
    user=request.user,
    address=address,
    total_price=total
)

    for item in cart.items.all():

       OrderItem.objects.create(
        order=order,
        product=item.product,
        quantity=item.quantity,
        price=item.product.price
    )

    cart.items.all().delete()

    return response

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = UserCreationForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )

@login_required
def profile(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'store/profile.html',
        {
            'orders': orders
        }
    )