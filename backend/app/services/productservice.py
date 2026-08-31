from app.data.products import products


def search_products(query: str):
    if not query:
        return []

    query = query.lower()

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
    return products.get(product_id)