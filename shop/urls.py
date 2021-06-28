from django.urls import path, include
from rest_framework.routers import format_suffix_patterns
from shop.views import *

product_list = ProductViewSet.as_view({
    "get": "list",
    "post": "create",
})

product_detail = ProductViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

review_list = ReviewViewSet.as_view({
    "get": "list",
    "post": "create",
})

review_detail = ReviewViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

collection_list = CollectionViewSet.as_view({
    "get": "list",
    "post": "create",
})

collection_detail = CollectionViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

order_list = OrderViewSet.as_view({
    "get": "list",
    "post": "create",
})

order_detail = OrderViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

user_list = UserViewSet.as_view({
    "get": "list",
    "post": "create",
})

user_detail = UserViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})


urlpatterns = format_suffix_patterns([
    path("products/", product_list, name="product-list"),
    path("products/<int:pk>/", product_detail, name="product-detail"),
    path("product-reviews/", review_list, name="review-list"),
    path("product-reviews/<int:pk>/", review_detail, name="review-detail"),
    path("product-collections/", collection_list, name="collection-list"),
    path("product-collections/<int:pk>/", collection_detail, name="collection-detail"),
    path("orders/", order_list, name="order-list"),
    path("orders/<int:pk>/", order_detail, name="order-detail"),
    path("profiles/", user_list, name="user-list"),
    path("profiles/<int:pk>/", user_detail, name="user-detail"),
])


