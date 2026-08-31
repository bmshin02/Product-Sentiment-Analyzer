import { useEffect, useState } from "react";

import { getProduct, searchProducts } from "./api/products";

import type { Product, ProductSearchResult } from "./types/product";

function App() {
  const [product, setProduct] = useState<Product | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ProductSearchResult[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadInitialProduct() {
      try {
        const data = await getProduct("airpods-pro");
        setProduct(data);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        }
      }
    }

    loadInitialProduct();
  }, []);

  async function handleSearch() {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    try {
      setError("");

      const data = await searchProducts(query);

      setResults(data);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      }
    }
  }

  async function handleSelectProduct(productId: string) {
    try {
      setError("");

      const data = await getProduct(productId);

      setProduct(data);
      setResults([]);
      setQuery("");
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      }
    }
  }

  return (
    <main>
      <h1>Reddit Product Intelligence</h1>

      <section>
        <input
          type="text"
          placeholder="Search for a product..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />

        <button onClick={handleSearch}>Search</button>

        {results.length > 0 && (
          <ul>
            {results.map((result) => (
              <li key={result.id}>
                <button onClick={() => handleSelectProduct(result.id)}>
                  {result.name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {error && <p>{error}</p>}

      {product && (
        <>
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
        </>
      )}
    </main>
  );
}

export default App;
