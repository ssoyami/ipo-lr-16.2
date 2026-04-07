from django.shortcuts import render
from django.http import HttpResponse


def about_author(request):
    return HttpResponse("Эта страница об авторе. Автор Санкевич Яна Александрона.")

def about_shop(request):
    return HttpResponse("Это страница о магазине. Это магазин масок и костюмов для праздников. (:")

def main_page(request):
    return render(request, 'store/index.html')

