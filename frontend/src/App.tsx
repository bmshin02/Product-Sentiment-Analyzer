import { useEffect, useState } from "react";

import { getProduct } from "./api/products";

import InsightList from "./components/insightlist";
import ProductHeader from "./components/productheader";
import ProductSearch from "./components/productsearch";
import SentimentSummary from "./components/sentimentsummary";

import type { Product } from "./types/product";

function App() {
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadInitialProduct() {
      try {
        const data = await getProduct("airpods-pro");
        setProduct(data);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        }
      } finally {
        setIsLoading(false);
      }
    }

    loadInitialProduct();
  }, []);

  async function loadProduct(productId: string) {
    try {
      setIsLoading(true);
      setError("");
      setProduct(null);

      const data = await getProduct(productId);

      setProduct(data);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="hero">
        <h1>Reddit Product Intelligence</h1>

        <p>Understand what consumers actually think about products.</p>

        <ProductSearch onSelectProduct={loadProduct} />
      </header>

      {error && <p className="error-message">{error}</p>}

      {isLoading && <p className="loading-message">Loading product...</p>}

      {product && !isLoading && (
        <div className="dashboard">
          <ProductHeader
            name={product.name}
            reviewsAnalyzed={product.reviews_analyzed}
          />

          <SentimentSummary
            positive={product.sentiment.positive}
            neutral={product.sentiment.neutral}
            negative={product.sentiment.negative}
          />

          <div className="insight-grid">
            <InsightList title="Top Positives" items={product.top_positives} />

            <InsightList
              title="Top Complaints"
              items={product.top_complaints}
            />
          </div>
        </div>
      )}
    </main>
  );
}

export default App;
