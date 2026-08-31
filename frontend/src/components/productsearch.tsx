import { useState } from "react";

import { searchProducts } from "../api/products";
import type { ProductSearchResult } from "../types/product";

type ProductSearchProps = {
  onSelectProduct: (productId: string) => void;
};

function ProductSearch({ onSelectProduct }: ProductSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ProductSearchResult[]>([]);
  const [error, setError] = useState("");

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

  function handleSelect(productId: string) {
    onSelectProduct(productId);

    setQuery("");
    setResults([]);
  }

  return (
    <div className="search-container">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search for a product..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />

        <button onClick={handleSearch}>Search</button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {results.length > 0 && (
        <ul className="search-results">
          {results.map((result) => (
            <li key={result.id}>
              <button onClick={() => handleSelect(result.id)}>
                {result.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ProductSearch;
