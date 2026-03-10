from django.urls import path, include
from . import views

urlpatterns = [
    path('about/', views.about_author, name='about_author'),
    path('shop-info/', views.about_shop, name='about_shop'),
    path('', views.main_page, name='main'),
 
]