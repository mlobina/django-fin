from django_filters import rest_framework as filters
from shop.models import Product, ProductReview, Order


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="contains")
    description = filters.CharFilter(field_name="description", lookup_expr="contains")
    price = filters.RangeFilter(field_name="price")

    class Meta:
        model = Product
        fields = ["name", "description", "price"]


class ReviewFilter(filters.FilterSet):
    user = "user__id"
    product = filters.NumberFilter(field_name="product__id")
    created_at = filters.DateFromToRangeFilter(field_name="created")

    class Meta:
        model = ProductReview
        fields = ["user", "product", "created"]


class OrderFilter(filters.FilterSet):
    created = filters.DateFromToRangeFilter(field_name="created")
    updated = filters.DateFromToRangeFilter(field_name="updated")
    total_cost = filters.RangeFilter(field_name="total_cost")
    product_id = filters.NumberFilter(field_name="positions__product_id")

    class Meta:
        model = Order
        fields = ("status", "total_cost", "updated", "created")
