import pytest
from fastapi.testclient import TestClient

from app.data.products import products
from app.main import app
from app.schemas.product import Product

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_without_query_returns_empty_list():
    assert client.get("/products").json() == []
    assert client.get("/products", params={"query": ""}).json() == []


def test_search_matches_partial_case_insensitive():
    response = client.get("/products", params={"query": "AIRPODS"})

    assert response.status_code == 200
    assert response.json() == [{"id": "airpods-pro", "name": "AirPods Pro"}]


def test_search_with_no_match_returns_empty_list():
    response = client.get("/products", params={"query": "zzz"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("query", [" ", "   "])
def test_search_whitespace_only_returns_empty_list(query):
    response = client.get("/products", params={"query": query})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("query", ["(", "a&b", "%", ".*", "\\"])
def test_search_special_characters_do_not_error(query):
    response = client.get("/products", params={"query": query})

    assert response.status_code == 200
    assert response.json() == []


def test_get_product():
    response = client.get("/products/airpods-pro")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "airpods-pro"
    assert Product(**body).name == "AirPods Pro"


@pytest.mark.parametrize("product_id", list(products))
def test_every_fixture_product_is_served(product_id):
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert Product(**response.json()).id == product_id


def test_unknown_product_returns_404():
    response = client.get("/products/nope")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


@pytest.mark.parametrize("product_id", ["a" * 5000, "%20"])
def test_odd_product_ids_return_404(product_id):
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_path_traversal_product_id_returns_404():
    response = client.get("/products/..%2Fetc")

    assert response.status_code == 404


def test_cors_allows_local_frontend_origin():
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_does_not_allow_unknown_origin():
    response = client.get("/health", headers={"Origin": "https://evil.example"})

    assert "access-control-allow-origin" not in response.headers
