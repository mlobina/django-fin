import pytest
from django.urls import reverse
import random
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_products_list(user_api_client, product_factory):
    products_list = product_factory()
    url = reverse("product-list")

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {product.id for product in products_list}
    response_ids = {product["id"] for product in resp_json}
    assert response_ids == expected_ids


@pytest.mark.django_db
def test_product_retrieve(user_api_client, product_factory):
    product = product_factory(min_amount=1, max_amount=1)[0]
    url = reverse("product-detail", args=[product.id])

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert product.id == resp_json["id"]


@pytest.mark.django_db
def test_products_filter_by_price(user_api_client, product_factory):
    random_product_price = str(random.choice(product_factory()).price)
    url = reverse("product-list")

    resp = user_api_client.get(url, {"price_min": random_product_price, "price_max": random_product_price})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    prices = {product["price"] for product in resp_json}
    check_price = set(filter(lambda x: x == random_product_price, prices))
    assert prices == check_price


@pytest.mark.django_db
def test_products_filter_by_name(user_api_client, product_factory):
    random_product_name = random.choice(product_factory()).name
    url = reverse("product-list")

    resp = user_api_client.get(url, {"name": random_product_name})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    names = {product["name"] for product in resp_json}
    check_names = set(filter(lambda x: x == random_product_name, names))
    assert names == check_names


@pytest.mark.django_db
def test_products_filter_by_description(user_api_client, product_factory):
    random_product_description = random.choice(product_factory()).description
    url = reverse("product-list")

    resp = user_api_client.get(url, {"description": random_product_description})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    descriptions = {product["description"] for product in resp_json}
    check_descriptions = set(filter(lambda x: x == random_product_description, descriptions))
    assert descriptions == check_descriptions


@pytest.mark.django_db
def test_products_create_by_user(product_factory, user_api_client, product_create_payload):
    url = reverse("product-list")

    resp = user_api_client.post(url, data=product_create_payload, format="json")

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_products_create_by_admin(product_factory, admin_api_client, product_create_payload):
    url = reverse("product-list")

    resp = admin_api_client.post(url, data=product_create_payload, format="json")
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json["name"] == product_create_payload["name"]


@pytest.mark.django_db
def test_products_update_by_user(product_factory, user_api_client):
    product = product_factory(min_amount=1, max_amount=1, name="product")[0]

    url = reverse("product-detail", args=[product.id])
    payload = {
        "name": f'test_{product.name}'
    }

    resp = user_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_products_update_by_admin(product_factory, admin_api_client):
    product = product_factory(min_amount=1, max_amount=1, name="product")[0]

    url = reverse("product-detail", args=[product.id])
    payload = {
        "name": f'test_{product.name}'
    }

    resp = admin_api_client.patch(url, data=payload)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert payload["name"] == resp_json["name"]


@pytest.mark.django_db
def test_products_delete_by_user(product_factory, user_api_client):
    random_product = random.choice(product_factory())
    url = reverse("product-detail", args=[random_product.id])

    resp = user_api_client.delete(url)

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_products_delete_by_admin(product_factory, admin_api_client):
    random_product = random.choice(product_factory())
    url = reverse("product-detail", args=[random_product.id])

    resp = admin_api_client.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [product["id"] for product in admin_api_client.get(reverse("product-list")).json()]
    assert random_product.id not in existing_ids
