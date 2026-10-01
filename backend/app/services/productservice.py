from app.data.products import products


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

    return {"id": product_id, **product}
