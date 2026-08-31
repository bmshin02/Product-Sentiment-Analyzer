from fastapi import APIRouter, HTTPException

from app.schemas.product import Product, ProductSearchResult
from app.services.productservice import (
    get_product,
    search_products,
)

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get(
    "",
    response_model=list[ProductSearchResult],
)
def search_products_route(query: str = ""):
    return search_products(query)


@router.get(
    "/{product_id}",
    response_model=Product,
)
def get_product_route(product_id: str):
    product = get_product(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product