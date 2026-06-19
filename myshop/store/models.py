from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"


class Manufacturer(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название"
    )

    country = models.CharField(
        max_length=100,
        verbose_name="Страна"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"


class Product(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )

    description = models.TextField(
        verbose_name="Описание"
    )

    photo = models.ImageField(
        upload_to="products/",
        verbose_name="Фото товара"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )

    stock_quantity = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Количество на складе"
    )

    categories = models.ManyToManyField(
    Category,
    verbose_name="Категории товаров"
)

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        verbose_name="Производитель"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def total_price(self):
        return sum(item.item_price() for item in self.items.all())

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )

    quantity = models.PositiveIntegerField(
        verbose_name="Количество"
    )

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"

    def item_price(self):
        return self.product.price * self.quantity

    def clean(self):
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(
                "Количество товара превышает остаток на складе."
            )

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"