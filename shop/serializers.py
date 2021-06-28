from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from django.db.models import ObjectDoesNotExist
from shop.models import Product, ProductReview, Collection, OrderProductPosition, Order, CollectionProduct


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для объектов модели User
    """

    class Meta:
        model = User
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для реализации действий  над объектами модели Product
    """

    class Meta:
        model = Product
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для реализации действий  над объектами модели ProductReview
    """
    user = serializers.IntegerField(read_only=True, source="user.id")

    class Meta:
        model = ProductReview
        fields = "__all__"

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, attrs):
        """
        Валидация соблюдения ограничения: 1 пользователь не может оставлять более 1го отзыва
        """
        if self.context["view"].action == "create":
            user = self.context["request"].user
            product = attrs["product"]
            existing_review = ProductReview.objects.filter(user=user, product=product)
            if existing_review:
                raise ValidationError({'error': 'К товару можно оставлять только 1 отзыв'})
            attrs["user"] = user
        elif self.context["view"].action in ["update", "partial_update"]:
            allowed_fields = {"rating", "text"}
            if attrs.keys() - allowed_fields:
                raise ValidationError({'error': f'Допустимые поля для изменения: {", ".join(sorted(allowed_fields))}'})

        return attrs


class CollectionProductSerializer(serializers.Serializer):
    """
    Сериализатор для поля products в CollectionSerializer
    """
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.CharField(source="product.price", read_only=True)


class CollectionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для реализации действий  над объектами модели Collection
    """
    products_list = CollectionProductSerializer(many=True, required=True)

    class Meta:
        model = Collection
        fields = "__all__"

    def validate(self, attrs):
        products_list = attrs.get("products_list")
        if self.context["view"].action == "create":

            if not products_list:
                raise ValidationError({"products": "Не указан список товаров"})

            products_ids_set = {product["product_id"].id for product in products_list}
            if len(products_ids_set) != len(products_list):
                raise ValidationError({"products": "В подборке повторяются одни и те же товары"})

        return attrs

    def create(self, validated_data):
        """
        Метод для создания объектов модели Collection
        """
        products_list = validated_data.pop("products_list")
        collection = super().create(validated_data)

        products_objs = [Product.objects.get(id=product["product_id"].id) for product in products_list]
        collection.products.add(*products_objs)

        return collection

    def update(self, instance, validated_data):
        products_list = validated_data.get("products_list")

        if products_list:
            existing_products = instance.products.all()
            new_products = [product["product_id"] for product in products_list if
                            product["product_id"] not in existing_products]

            if new_products:
                instance.products.add(*new_products)
            validated_data.pop("products_list")

        instance = super().update(instance, validated_data)
        return instance


class OrderProductPositionSerializer(serializers.Serializer):
    """
    Сериализатор для поля products в OrderSerializer
    """
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),
                                                    source="product.id")
    name = serializers.CharField(source="product.name", read_only=True)
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для реализации действий  над объектами модели Order
    """
    positions = OrderProductPositionSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["user", "total_cost"]

    def validate(self, attrs):
        user = self.context["request"].user
        if self.context["view"].action == "create":
            positions = attrs.get("positions")

            if not positions:
                raise ValidationError(f"Вы не указали товары в заказе")

            price = (position["product"]["id"].price for position in positions)
            quantity = (position["quantity"] for position in positions)
            total_cost = round(sum(price * quantity for price, quantity in zip(price, quantity)), 2)

            attrs["user"] = user
            attrs["total_cost"] = total_cost

        elif self.context["view"].action in ["update", "partial_update"]:

            allowed_fields = {"positions"}
            allowed_fields.add("status") if user.is_staff else allowed_fields
            if attrs.keys() - allowed_fields:
                raise ValidationError({'error': f'Допустимые поля для изменения: {", ".join(sorted(allowed_fields))}'})

        return attrs

    def create(self, validated_data):
        positions = validated_data.pop("positions")
        order = super().create(validated_data)

        positions_objs = [
            OrderProductPosition(
                quantity=position["quantity"],
                product=position["product"]["id"],
                order=order
            )
            for position in positions
        ]

        OrderProductPosition.objects.bulk_create(positions_objs)
        return order

    def update(self, instance, validated_data):
        positions = validated_data.get("positions")

        if positions:
            for position in positions:
                product_id = position["product"]["id"].id
                quantity = position["quantity"]
                try:
                    position_obj = OrderProductPosition.objects.get(product_id=product_id, order=instance)
                    position_obj.quantity = quantity
                    position_obj.save()
                except ObjectDoesNotExist:
                    OrderProductPosition.objects.create(product_id=product_id, quantity=quantity, order=instance)
            validated_data.pop("positions")

        total_cost = round(sum(position.product.price * position.quantity for position in
                               OrderProductPosition.objects.filter(order=instance)), 2)

        validated_data["total_cost"] = total_cost
        instance = super().update(instance, validated_data)

        return instance
