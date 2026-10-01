import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { searchProducts } from "../api/products";
import ProductSearch from "./productsearch";

vi.mock("../api/products", () => ({
  searchProducts: vi.fn(),
}));

const mockedSearch = vi.mocked(searchProducts);

const AIRPODS = { id: "airpods-pro", name: "AirPods Pro" };

function setup() {
  const onSelectProduct = vi.fn();
  const user = userEvent.setup();

  render(<ProductSearch onSelectProduct={onSelectProduct} />);

  return { onSelectProduct, user };
}

async function search(user: ReturnType<typeof userEvent.setup>, text: string) {
  const input = screen.getByPlaceholderText("Search for a product...");

  await user.clear(input);
  if (text) {
    await user.type(input, text);
  }
  await user.click(screen.getByRole("button", { name: "Search" }));
}

describe("ProductSearch", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("lists matching products after a search", async () => {
    mockedSearch.mockResolvedValue([AIRPODS]);
    const { user } = setup();

    await search(user, "airpods");

    expect(
      await screen.findByRole("button", { name: "AirPods Pro" }),
    ).toBeInTheDocument();
    expect(mockedSearch).toHaveBeenCalledWith("airpods");
  });

  it("selecting a result reports its id and resets the search", async () => {
    mockedSearch.mockResolvedValue([AIRPODS]);
    const { onSelectProduct, user } = setup();

    await search(user, "airpods");
    await user.click(await screen.findByRole("button", { name: "AirPods Pro" }));

    expect(onSelectProduct).toHaveBeenCalledWith("airpods-pro");
    expect(screen.getByPlaceholderText("Search for a product...")).toHaveValue("");
    expect(
      screen.queryByRole("button", { name: "AirPods Pro" }),
    ).not.toBeInTheDocument();
  });

  it.each(["", "   "])("does not search for %j", async (text) => {
    const { user } = setup();

    await search(user, text);

    expect(mockedSearch).not.toHaveBeenCalled();
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("shows no list and no error when nothing matches", async () => {
    mockedSearch.mockResolvedValue([]);
    const { user } = setup();

    await search(user, "zzz");

    await vi.waitFor(() => expect(mockedSearch).toHaveBeenCalledWith("zzz"));
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
    expect(screen.queryByText("Failed to search products")).not.toBeInTheDocument();
  });

  it("shows the error message when the search fails", async () => {
    mockedSearch.mockRejectedValue(new Error("Failed to search products"));
    const { user } = setup();

    await search(user, "airpods");

    expect(await screen.findByText("Failed to search products")).toBeInTheDocument();
  });

  it("clears an earlier error after a successful search", async () => {
    mockedSearch.mockRejectedValueOnce(new Error("Failed to search products"));
    mockedSearch.mockResolvedValueOnce([AIRPODS]);
    const { user } = setup();

    await search(user, "airpods");
    expect(await screen.findByText("Failed to search products")).toBeInTheDocument();

    await search(user, "airpods");

    expect(
      await screen.findByRole("button", { name: "AirPods Pro" }),
    ).toBeInTheDocument();
    expect(screen.queryByText("Failed to search products")).not.toBeInTheDocument();
  });
});
