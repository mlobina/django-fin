from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from shop.models import Product, ProductReview, Collection, Order
from shop.serializers import ProductSerializer, ReviewSerializer, CollectionSerializer, OrderSerializer, UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from shop.filters import ProductFilter, ReviewFilter, OrderFilter
from shop.permissions import IsOwnerOrAdmin


class ProductViewSet(viewsets.ModelViewSet):
    """
    Обработчик для объектов модели Product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_permissions(self):
        """
        Создавать товары могут только админы. Смотреть могут все пользователи
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAdminUser]
            return [permission() for permission in permission_classes]
        return []


class ReviewViewSet(viewsets.ModelViewSet):
    """
      Обработчик для объектов модели ProductReview
    """
    queryset = ProductReview.objects.select_related("user", "product")
    serializer_class = ReviewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ReviewFilter

    def get_permissions(self):
        """
        Оставлять отзыв к товару могут только авторизованные пользователи.
        Пользователь может обновлять и удалять только свой собственный отзыв.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return []


class CollectionViewSet(viewsets.ModelViewSet):
    """
       Обработчик для объектов модели Collection
     """
    queryset = Collection.objects.prefetch_related("products")
    serializer_class = CollectionSerializer

    def get_permissions(self):
        """
        Создавать подборки могут только админы, остальные пользователи могут только их смотреть.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAdminUser]
            return [permission() for permission in permission_classes]
        return []


class OrderViewSet(viewsets.ModelViewSet):
    """
       Обработчик для объектов модели Order
     """
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_permissions(self):
        """
        Создавать заказы могут только авторизованные пользователи.
        Админы могут получать все заказы, остальное пользователи только свои.
        """
        if self.action in ["list", "retrieve", "create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return []

    def get_queryset(self):
        """
        Админы могут получать все заказы, остальное пользователи только свои.
        """
        if self.request.user.is_staff:
            return Order.objects.prefetch_related("positions").all()
        return Order.objects.prefetch_related("positions").filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """
    Обработчик для объектов модели User
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]
