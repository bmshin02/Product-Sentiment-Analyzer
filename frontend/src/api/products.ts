import type { Product } from "../types/product";

const API_URL = import.meta.env.VITE_API_URL;

export async function getProduct(productId: string): Promise<Product> {
  const response = await fetch(`${API_URL}/products/${productId}`);

  if (!response.ok) {
    throw new Error("Failed to load product");
  }

  return response.json();
}
