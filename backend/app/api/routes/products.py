from fastapi import APIRouter, HTTPException

from app.data.products import products
from app.schemas.product import Product, ProductSearchResult

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get(
    "",
    response_model=list[ProductSearchResult],
)
def search_products(query: str = ""):
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


@router.get(
    "/{product_id}",
    response_model=Product,
)
def get_product(product_id: str):
    product = products.get(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product