from app.data.comments import comments
from app.data.products import products
from app.services.analysis.sentiment import aggregate_sentiment
from app.services.analysis.wordsentiment import get_sentiment_words


def search_products(query: str):
    query = query.strip().lower()

    if not query:
        return []

    results = []

    for product_id, product in products.items():
        if query in product["name"].lower():
            results.append(
                {
                    "id": product_id,
                    "name": product["name"],
                }
            )

    return results


def get_product(product_id: str):
    product = products.get(product_id)

    if product is None:
        return None

    product_comments = comments.get(product_id, [])
    positives, negatives = get_sentiment_words(product_comments)

    return {
        "id": product_id,
        "name": product["name"],
        "reviews_analyzed": len(product_comments),
        "sentiment": aggregate_sentiment(product_comments),
        "top_positives": positives,
        "top_complaints": negatives,
    }
