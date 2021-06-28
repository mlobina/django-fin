import pytest
from django.urls import reverse
import random
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT



@pytest.mark.django_db
def test_reviews_list(user_api_client, review_factory):
    reviews_list = review_factory()
    url = reverse("review-list")

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {review.id for review in reviews_list}
    response_ids = {review["id"] for review in resp_json}
    assert response_ids == expected_ids


@pytest.mark.django_db
def test_review_retrieve(user_api_client, review_factory):
    review = review_factory()[0]
    url = reverse("review-detail", args=[review.id])

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert review.id == resp_json["id"]


@pytest.mark.django_db
def test_reviews_filter_by_user_id(user_api_client, review_factory):
    random_review_user_id = random.choice(review_factory()).user_id
    url = reverse("review-list")

    resp = user_api_client.get(url, {"user": random_review_user_id})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    user_id = {review["user"] for review in resp_json}
    check_user_id = set(filter(lambda x: x == random_review_user_id, user_id))
    assert user_id == check_user_id


@pytest.mark.django_db
def test_reviews_filter_by_creation_date(user_api_client, review_factory):
    random_review_creation_date = random.choice(review_factory()).created
    url = reverse("review-list")

    resp = user_api_client.get(url, {"created": random_review_creation_date})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    creation_dates = {review["created"] for review in resp_json}
    check_review_creation_date = set(filter(lambda x: x == random_review_creation_date.isoformat(), creation_dates))
    assert creation_dates == check_review_creation_date


@pytest.mark.django_db
def test_reviews_filter_by_product_id(user_api_client, review_factory):
    random_review_product_id = random.choice(review_factory()).product.id
    url = reverse("review-list")

    resp = user_api_client.get(url, {"product": random_review_product_id})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    product_ids = {review["product"] for review in resp_json}
    check_product_id = set(filter(lambda x: x == random_review_product_id, product_ids))
    assert product_ids == check_product_id


@pytest.mark.django_db
def test_reviews_create(user_api_client, review_create_payload):
    url = reverse("review-list")

    resp = user_api_client.post(url, data=review_create_payload, format="json")
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json["product"] == review_create_payload["product"] and resp_json["text"] == review_create_payload[
        "text"] and resp_json["rating"] == review_create_payload["rating"]


@pytest.mark.django_db
def test_review_update_by_owner(review_factory, user_api_client, user):
    review = review_factory()[0]
    review.user = user

    url = reverse("review-detail", args=[review.id])
    payload = {
        "text": f'test_{review.text}'
    }

    resp = user_api_client.patch(url, data=payload)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert payload["text"] == resp_json["text"]


@pytest.mark.django_db
def test_review_update_by_admin(review_factory, admin_api_client):
    review = review_factory()[0]

    url = reverse("review-detail", args=[review.id])
    payload = {
        "text": f'test_{review.text}'
    }

    resp = admin_api_client.patch(url, data=payload)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert payload["text"] == resp_json["text"]


@pytest.mark.django_db
def test_review_update_by_another_user(review_factory, another_user_api_client, user):
    review = review_factory()[0]
    review.user = user

    url = reverse("review-detail", args=[review.id])
    payload = {
        "text": f'test_{review.text}'
    }

    resp = another_user_api_client.patch(url, data=payload)
    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_review_delete_by_admin(review_factory, admin_api_client):
    random_review = random.choice(review_factory())

    url = reverse("review-detail", args=[random_review.id])

    resp = admin_api_client.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [product["id"] for product in admin_api_client.get(reverse("review-list")).json()]
    assert random_review.id not in existing_ids


@pytest.mark.django_db
def test_review_delete_by_owner(review_factory, user_api_client, user):
    random_review = random.choice(review_factory())
    random_review.user = user

    url = reverse("review-detail", args=[random_review.id])

    resp = user_api_client.delete(url)
    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [product["id"] for product in user_api_client.get(reverse("review-list")).json()]
    assert random_review.id not in existing_ids


@pytest.mark.django_db
def test_review_delete_by_another_user(review_factory, another_user_api_client, user):
    random_review = random.choice(review_factory())
    random_review.user = user

    url = reverse("review-detail", args=[random_review.id])

    resp = another_user_api_client.delete(url)
    assert resp.status_code == HTTP_403_FORBIDDEN