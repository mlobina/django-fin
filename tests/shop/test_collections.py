import pytest
from django.urls import reverse
import random
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_collections_list(user_api_client, collection_factory):
    collections_list = collection_factory()
    url = reverse("collection-list")

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {collection.id for collection in collections_list}
    response_ids = {collection["id"] for collection in resp_json}
    assert response_ids == expected_ids


@pytest.mark.django_db
def test_collection_retrieve(collection_factory, user_api_client):
    collection = collection_factory(min_amount=1, max_amount=1)[0]
    url = reverse("collection-detail", args=[collection.id])

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert collection.id == resp_json["id"]


@pytest.mark.django_db
def test_collection_create_by_admin(admin_api_client, collection_create_payload):
    url = reverse("collection-list")

    resp = admin_api_client.post(url, data=collection_create_payload, format="json")
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert collection_create_payload["name"] == resp_json["name"]
    assert collection_create_payload["text"] == resp_json["text"]
    assert collection_create_payload["products_list"][0]["product_id"] == resp_json["products_list"][0]["product_id"]

@pytest.mark.django_db
def test_collection_create_by_user(user_api_client, collection_create_payload):
    url = reverse("collection-list")

    resp = user_api_client.post(url, data=collection_create_payload, format="json")
    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_collections_update_by_admin(collection_factory, admin_api_client):
    collection = collection_factory(min_amount=1, max_amount=1, name="collection")[0]

    url = reverse("collection-detail", args=[collection.id])
    payload = {
        "name": f'test_{collection.name}'
    }

    resp = admin_api_client.patch(url, data=payload)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert payload["name"] == resp_json["name"]


@pytest.mark.django_db
def test_collections_update_by_user(collection_factory, user_api_client):
    collection = collection_factory(min_amount=1, max_amount=1, name="collection")[0]

    url = reverse("collection-detail", args=[collection.id])
    payload = {
        "name": f'test_{collection.name}'
    }

    resp = user_api_client.patch(url, data=payload)
    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_collections_delete_by_admin(collection_factory, admin_api_client):
    random_collection = random.choice(collection_factory())
    url = reverse("collection-detail", args=[random_collection.id])

    resp = admin_api_client.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [collection["id"] for collection in admin_api_client.get(reverse("collection-list")).json()]
    assert random_collection.id not in existing_ids


@pytest.mark.django_db
def test_collections_delete_by_user(collection_factory, user_api_client):
    random_collection = random.choice(collection_factory())
    url = reverse("collection-detail", args=[random_collection.id])

    resp = user_api_client.delete(url)
    assert resp.status_code == HTTP_403_FORBIDDEN
