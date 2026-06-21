from django.urls import path, include 
from . import views
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    ManufacturerViewSet,
    CartViewSet,
    CartItemViewSet
)
from .views import register

router = DefaultRouter()

router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cartitems', CartItemViewSet)

urlpatterns = [
    path('about/', views.about_author, name='about_author'),
    path('shop-info/', views.about_shop, name='about_shop'),
    path('', views.main_page, name='main'),

    path('catalog/', views.product_list, name='catalog'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('download_receipt/', views.download_receipt, name='download_receipt'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]
urlpatterns += [
    path('api/', include(router.urls)),
    path('register/', register, name='register')
]
