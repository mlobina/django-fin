from django.contrib import admin
from shop.models import *


class OrderProductPositionInline(admin.TabularInline):
    model = OrderProductPosition
    raw_id_fields = ['product']




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "price", "slug", "created", "updated")
    list_filter = ("name", "price")
    search_fields = ("slug", "id")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_cost", "created", "updated")
    list_filter = ("updated", "created")
    search_fields = ("user", "id", "status", "total_cost")
    inlines = [OrderProductPositionInline]


class CollectionProductInline(admin.TabularInline):
    model = CollectionProduct
    raw_id_fields = ['product']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "text", "created", "updated")
    list_filter = ("updated", "created")
    search_fields = ("slug", "id", )
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CollectionProductInline]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user",  "text", "product", "created", "updated")
    list_filter = ("updated", "created")
    search_fields = ("user", "id", )





