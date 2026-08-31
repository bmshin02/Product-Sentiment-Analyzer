from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.data.products import products

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products/{product_id}")
def get_product(product_id: str):
    product = products.get(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product

@app.get("/products")
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