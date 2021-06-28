from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class CommonInfo(models.Model):
    """
    Абстрактный базовый класс для дублирующихся полей в разных моделях
    """
    created = models.DateField(auto_now_add=True,
                               verbose_name="дата создания",
                               )
    updated = models.DateField(auto_now=True,
                               verbose_name="дата обновления",
                               )

    class Meta:
        abstract = True


class OrderStatusChoices(models.TextChoices):
    """
    Модель TextChoices создает choices set для назначения поля status модели Order
    """
    NEW = "New", "Создан"
    IN_PROGRESS = "In_progress", "В обработке"
    DONE = "Done", "Выполнен"


class Product(CommonInfo):
    """
    Модель для описания товаров
    """
    name = models.CharField(max_length=200,
                            blank=False,
                            verbose_name="Наименование",
                            )
    description = models.TextField(blank=True,
                                   verbose_name="Описание",
                                   )
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                blank=False,
                                null=False,
                                verbose_name="Цена",
                                )
    slug = models.SlugField(max_length=200)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["name", "price"]

    def __str__(self):
        return f"name:{self.name} - id:{self.id}"


class Order(CommonInfo):
    """
    Модель для описания заказов
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="products",
                             verbose_name="Покупатель",
                             on_delete=models.DO_NOTHING,
                             )
    products = models.ManyToManyField(Product,
                                      through="OrderProductPosition",
                                      verbose_name="Позиция",
                                      )
    status = models.TextField(choices=OrderStatusChoices.choices,
                              default=OrderStatusChoices.NEW,
                              verbose_name="Статус",
                              )
    total_cost = models.FloatField(
        validators=[
            MinValueValidator(0)
        ]
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-updated", "-created"]

    def __str__(self):
        return f"id:{self.id} - user:{self.user} - status:{self.status} - items:{len(self.positions.all())}"


class OrderProductPosition(models.Model):
    """
    Модель для ManyToMany связи между моделями Product и Order,
    описывает поле products в модели Order
    """
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                )
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name="positions",
                              )
    quantity = models.IntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    class Meta:
        db_table = "order_product_position"
        verbose_name = "Позиция в заказе"
        verbose_name_plural = "Позиции в заказе"
        ordering = ["-quantity"]


class Collection(CommonInfo):
    """
    Модель для описания подборки товаров
    """
    name = models.CharField(max_length=200,
                            blank=False,
                            verbose_name="Наименование",
                            )
    slug = models.SlugField(max_length=200)
    text = models.TextField(blank=True,
                            verbose_name="Описание",
                            )
    products = models.ManyToManyField(Product,
                                      through="CollectionProduct")

    class Meta:
        verbose_name = "Подборка"
        verbose_name_plural = "Подборки"
        ordering = ["-updated", "-created"]

    def __str__(self):
        return f"name:{self.name} - id:{self.id}"


class CollectionProduct(models.Model):
    """
    Модель для ManyToMany связи между моделями Product и Collection,
    описывает поле products в модели Collection
    """
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                )
    collection = models.ForeignKey(Collection,
                                   on_delete=models.CASCADE,
                                   related_name="products_list",
                                   )

    class Meta:
        db_table = "collection_product"


class ProductRatingChoices(models.IntegerChoices):
    """
    Модель IntegerChoices создает choices set для назначения поля rating модели ProductReview
    """
    VERY_BAD = 1, "Very bad"
    BAD = 2, "Bad"
    NOT_BAD = 3, "Not bad"
    GOOD = 4, "Good"
    VERY_GOOD = 5, "Very good"


class ProductReview(CommonInfo):
    """
    Модель для описания отзыва на товары
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="Покупатель",
                             on_delete=models.DO_NOTHING,
                             related_name="reviews",
                             )
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                )
    text = models.TextField(blank=True,
                            verbose_name="Отзыв",
                            )
    rating = models.IntegerField(choices=ProductRatingChoices.choices,
                                 default=5,
                                 )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-updated", "-created"]

    def __str__(self):
        return f"id:{self.id} - user:{self.user}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
