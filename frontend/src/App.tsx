import { useEffect, useState } from "react";

import { getProduct } from "./api/products";
import type { Product } from "./types/product";

function App() {
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProduct() {
      try {
        const data = await getProduct("airpods-pro");
        setProduct(data);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        }
      }
    }

    loadProduct();
  }, []);

  if (error) {
    return <p>{error}</p>;
  }

  if (!product) {
    return <p>Loading product...</p>;
  }

  return (
    <main>
      <h1>Reddit Product Intelligence</h1>

      <section>
        <h2>{product.name}</h2>
        <p>{product.reviews_analyzed} reviews analyzed</p>
      </section>

      <section>
        <h3>Sentiment</h3>

        <p>Positive: {Math.round(product.sentiment.positive * 100)}%</p>
        <p>Neutral: {Math.round(product.sentiment.neutral * 100)}%</p>
        <p>Negative: {Math.round(product.sentiment.negative * 100)}%</p>
      </section>

      <section>
        <h3>Top Positives</h3>

        <ul>
          {product.top_positives.map((positive) => (
            <li key={positive}>{positive}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Top Complaints</h3>

        <ul>
          {product.top_complaints.map((complaint) => (
            <li key={complaint}>{complaint}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}

export default App;
