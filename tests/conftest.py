
import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from random import randint



# Общие фикстуры для api:

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username="user", password="password")


@pytest.fixture
def user_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


@pytest.fixture
def user_api_client(user_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
    return client


@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create(username="another_user", password="password")


@pytest.fixture
def another_user_token(another_user):
    token, _ = Token.objects.get_or_create(user=another_user)
    return token.key


@pytest.fixture
def another_user_api_client(another_user_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {another_user_token}')
    return client


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create(username="admin", password="password", is_staff=True)


@pytest.fixture
def admin_token(admin):
    token, _ = Token.objects.get_or_create(user=admin)
    return token.key


@pytest.fixture
def admin_api_client(admin_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token}')
    return client


# Фикстуры для тестов эндпоинта products:

@pytest.fixture
def product_factory():
    def factory(min_amount=1, max_amount=20, **kwargs):
        return baker.make("Product", _quantity=randint(min_amount, max_amount), **kwargs)

    return factory


@pytest.fixture
def product_create_payload():
    return {
        "name": "test",
        "description": "test",
        "price": 100,
        "slug": "test"
    }


# Фикстуры для тестов эндпоинта product-reviews:

@pytest.fixture
def review_factory(user, product_factory):
    def factory(min_amount=1, max_amount=20, **kwargs):
        return baker.make("ProductReview", user=user, _quantity=randint(min_amount, max_amount), **kwargs)

    return factory


@pytest.fixture
def review_create_payload(product_factory):
    product = product_factory(min_amount=1, max_amount=1)[0]
    return {
        "product": product.id,
        "text": "test",
        "rating": 4
    }


# Фикстуры для тестов эндпоинта orders:

@pytest.fixture
def order_factory(user):
    def factory(min_amount=1, max_amount=20, **kwargs):
        return baker.make("Order", user=user, _quantity=randint(min_amount, max_amount), **kwargs, make_m2m=True)

    return factory


@pytest.fixture
def order_create_payload(product_factory):
    product = product_factory(min_amount=1, max_amount=1)[0]
    return {"positions": [
        {"product_id": product.id, "quantity": 1}
    ]
    }


@pytest.fixture
def order_update_payload(order_factory):
    order = order_factory()[0]
    url = reverse("order-detail", args=[order.id])

    product_id = order.positions.first().product_id
    payload = {
        "positions": [
            {
                "product_id": product_id,
                "quantity": randint(1, 10)
            }
        ]
    }
    return url, payload


# Фикстуры для тестов эндпоинта collections:

@pytest.fixture
def collection_factory(user):
    def factory(min_amount=1, max_amount=20, **kwargs):
        return baker.make("Collection", _quantity=randint(min_amount, max_amount), **kwargs, make_m2m=True)

    return factory


@pytest.fixture
def collection_create_payload(product_factory):
    product = product_factory(min_amount=1, max_amount=1)[0]

    return {
        "name": "test_collection",
        "text": "test",
        "slug": "test",
        "products_list": [
            {
                "product_id": product.id
            },

        ]
    }


