import pytest
from django.urls import reverse
import random
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from shop.models import OrderStatusChoices


@pytest.mark.django_db
def test_order_list(order_factory, user_api_client):
    orders_list = order_factory()
    url = reverse("order-list")

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {order.id for order in orders_list}
    response_ids = {order["id"] for order in resp_json}
    assert expected_ids == response_ids


@pytest.mark.django_db
def test_order_retrieve(order_factory, user_api_client):
    order = order_factory()[0]
    url = reverse("order-detail", args=[order.id])

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert order.id == resp_json["id"]


@pytest.mark.django_db
def test_order_filter_by_status(order_factory, admin_api_client):
    orders_list = order_factory()
    random_status = random.choices(OrderStatusChoices.values)[0]
    url = reverse("order-list")

    resp = admin_api_client.get(url, {"status": random_status})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {order.id for order in orders_list if order.status == random_status}
    resp_ids = {order.get("id") for order in resp_json}
    assert expected_ids == resp_ids


@pytest.mark.django_db
def test_order_filter_by_total_cost(order_factory, admin_api_client):
    random_total_cost = random.choices(order_factory())[0].total_cost
    url = reverse("order-list")

    resp = admin_api_client.get(url, {"total_cost_min": random_total_cost, "total_cost_max": random_total_cost})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    total_cost = {order["total_cost"] for order in resp_json}
    check_total_cost = set(filter(lambda x: x == random_total_cost, total_cost))
    assert total_cost == check_total_cost


@pytest.mark.django_db
def test_order_filter_by_creation_date(order_factory, admin_api_client):
    random_order_creation_date = random.choice(order_factory()).created
    url = reverse("order-list")

    resp = admin_api_client.get(url, {"created": random_order_creation_date})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    creation_dates = {order["created"] for order in resp_json}
    check_order_creation_date = set(filter(lambda x: x == random_order_creation_date.isoformat(), creation_dates))
    assert creation_dates == check_order_creation_date


@pytest.mark.django_db
def test_order_filter_by_update_date(order_factory, admin_api_client):
    random_order_update_date = random.choice(order_factory()).updated
    url = reverse("order-list")

    resp = admin_api_client.get(url, {"updated": random_order_update_date})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    update_dates = {order["updated"] for order in resp_json}
    check_order_update_date = set(filter(lambda x: x == random_order_update_date.isoformat(), update_dates))
    assert update_dates == check_order_update_date


@pytest.mark.django_db
def test_order_filter_by_product(order_factory, admin_api_client):
    random_order = random.choice(order_factory())
    random_product = random.choice(random_order.products.all())
    url = reverse("order-list")

    resp = admin_api_client.get(url, {"product_id": random_product.id})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    resp_orders = {order["id"] for order in resp_json}
    check_resp_orders = set()
    for order in resp_json:
        if [position for position in order["positions"] if position["product_id"] == random_product.id]:
            check_resp_orders.add(order["id"])
    assert resp_orders == check_resp_orders


@pytest.mark.django_db
def test_order_create(user_api_client, order_create_payload):
    url = reverse("order-list")
    product_id = order_create_payload["positions"][0]["product_id"]
    quantity = order_create_payload["positions"][0]["quantity"]

    resp = user_api_client.post(url, data=order_create_payload, format="json")
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json["positions"][0]["product_id"] == product_id and resp_json["positions"][0]["quantity"] == quantity


@pytest.mark.django_db
def test_order_update_by_owner(user_api_client, order_update_payload):
    url, payload = order_update_payload
    product_id = payload["positions"][0]["product_id"]
    quantity = payload["positions"][0]["quantity"]

    resp = user_api_client.patch(url, data=payload, format="json")
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    check_positions = [position["product_id"] for position in resp_json["positions"] if
                       position["product_id"] == product_id and position["quantity"] == quantity
                       ]
    assert check_positions


@pytest.mark.django_db
def test_order_update_by_another_user(another_user_api_client, order_update_payload):
    url, payload = order_update_payload

    resp = another_user_api_client.patch(url, data=payload, format="json")
    assert resp.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_order_update_by_admin(admin_api_client, order_update_payload):
    url, payload = order_update_payload
    product_id = payload["positions"][0]["product_id"]
    quantity = payload["positions"][0]["quantity"]

    resp = admin_api_client.patch(url, data=payload, format="json")
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    check_positions = [position["product_id"] for position in resp_json["positions"] if
                       position["product_id"] == product_id and position["quantity"] == quantity
                       ]
    assert check_positions


@pytest.mark.django_db
def test_order_delete_by_owner(user_api_client, order_factory):
    random_order = random.choices(order_factory())[0]
    url = reverse("order-detail", args=[random_order.id])

    resp = user_api_client.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [order["id"] for order in user_api_client.get(reverse("order-list")).json()]
    assert random_order.id not in existing_ids


@pytest.mark.django_db
def test_order_delete_by_another_user(another_user_api_client, order_factory):
    random_order = random.choices(order_factory())[0]
    url = reverse("order-detail", args=[random_order.id])

    resp = another_user_api_client.delete(url)
    assert resp.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_order_delete_by_admin(order_factory, admin_api_client):
    random_order = random.choices(order_factory())[0]
    url = reverse("order-detail", args=[random_order.id])

    resp = admin_api_client.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [order["id"] for order in admin_api_client.get(reverse("order-list")).json()]
    assert random_order.id not in existing_ids

