import type { Product, ProductSearchResult } from "../types/product";

const API_URL = import.meta.env.VITE_API_URL;

export async function getProduct(productId: string): Promise<Product> {
  const response = await fetch(`${API_URL}/products/${productId}`);

  if (!response.ok) {
    throw new Error("Failed to load product");
  }

  return response.json();
}

export async function searchProducts(
  query: string,
): Promise<ProductSearchResult[]> {
  const response = await fetch(
    `${API_URL}/products?query=${encodeURIComponent(query)}`,
  );

  if (!response.ok) {
    throw new Error("Failed to search products");
  }

  return response.json();
}
