import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getProduct, searchProducts } from "./products";

const fetchMock = vi.fn();

function respond(ok: boolean, body: unknown) {
  fetchMock.mockResolvedValue({ ok, json: async () => body } as Response);
}

describe("products api client", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("getProduct requests the product URL and returns the JSON body", async () => {
    const product = { id: "airpods-pro", name: "AirPods Pro" };
    respond(true, product);

    const result = await getProduct("airpods-pro");

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/products/airpods-pro");
    expect(result).toEqual(product);
  });

  it("getProduct throws on a non-OK response", async () => {
    respond(false, {});

    await expect(getProduct("nope")).rejects.toThrow("Failed to load product");
  });

  it("searchProducts encodes the query", async () => {
    respond(true, []);

    await searchProducts("a&b c");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/products?query=a%26b%20c",
    );
  });

  it("searchProducts returns the JSON body", async () => {
    const results = [{ id: "airpods-pro", name: "AirPods Pro" }];
    respond(true, results);

    expect(await searchProducts("airpods")).toEqual(results);
  });

  it("searchProducts throws on a non-OK response", async () => {
    respond(false, {});

    await expect(searchProducts("x")).rejects.toThrow("Failed to search products");
  });

  it("lets a network failure propagate", async () => {
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(searchProducts("x")).rejects.toThrow("Failed to fetch");
    await expect(getProduct("x")).rejects.toThrow("Failed to fetch");
  });
});
