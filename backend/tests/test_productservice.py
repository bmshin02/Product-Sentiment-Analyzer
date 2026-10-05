from app.schemas.product import Product
from app.services.productservice import get_product


def test_get_product_includes_id():
    product = get_product("airpods-pro")

    assert product["id"] == "airpods-pro"
    assert Product(**product).id == "airpods-pro"


def test_get_product_unknown_returns_none():
    assert get_product("does-not-exist") is None


def test_every_product_has_fixture_comments():
    from app.data.comments import comments
    from app.data.products import products

    for product_id in products:
        assert 15 <= len(comments[product_id]) <= 20


def test_get_product_computes_insights_from_comments():
    from app.data.comments import comments

    product = get_product("airpods-pro")

    assert product["reviews_analyzed"] == len(comments["airpods-pro"])
    assert product["top_positives"]
    assert product["top_complaints"]

    sentiment = product["sentiment"]
    total = sentiment.positive + sentiment.neutral + sentiment.negative
    assert abs(total - 1.0) < 1e-9
