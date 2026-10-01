# CI and Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add API tests, frontend tests and a GitHub Actions workflow so every push is checked automatically.

**Architecture:** Backend API tests use FastAPI's `TestClient` in-process. Frontend tests use Vitest with jsdom and Testing Library, colocated next to the code they test. One workflow file with two parallel jobs (`backend`, `frontend`) runs everything; it checks code only and never deploys.

**Tech Stack:** pytest, FastAPI `TestClient` (needs `httpx2`), Vitest 5, jsdom, @testing-library/react, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-01-ci-and-tests-design.md`

## Global Constraints

- Backend CI: Python 3.13; frontend CI: Node 22; triggers are `pull_request` and `push` to `main`; in-progress runs for the same ref are cancelled.
- CI only checks code. No deployment steps, no coverage thresholds, no Dependabot, no branch protection.
- No tests for `App.tsx`.
- Frontend tests must pass `npm run lint`, `tsc -b` and `npm run build`.
- Frontend `VITE_API_URL` is set to a dummy value for the CI build.
- **Spec deviation:** the spec says to add `httpx`. The pinned Starlette's `TestClient` raises `RuntimeError: ... requires the httpx2 package`, so this plan adds `httpx2==2.13.1` instead.
- Stage files by exact path in every commit. The working tree has unrelated uncommitted files (`README.md` edits, `CLAUDE.md` edits, Docker files); never use `git add -A` or `git add .`.
- Commit messages end with these trailers:
  ```
  Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348
  ```

## Review Focus

Inputs the spec implies but its listed tests don't cover, most likely to bite first. Each has a test in the task named in brackets.

1. **Whitespace-only `query`** (`/products?query=%20%20`): a reasonable person expects `[]`. Today every product name contains a space, so it returns all products. [Task 1; includes a one-line fix to `search_products`, a small behavior change beyond the spec]
2. **Special characters in `query`** (`(`, `a&b`, `%`): expect `[]`, not a 500. [Task 1; the frontend encoding side is in Task 4]
3. **Odd product ids** (`/products/..%2Fetc`, a very long id): expect 404 with `{"detail": "Product not found"}`, not a 500. [Task 1]
4. **A search with no matches** in the UI: expect no list rendered and no error. [Task 3]
5. **A stale error after recovery**: after a failed search then a successful one, the error message must disappear. [Task 3]
6. **Network failure** (`fetch` rejects rather than returning non-OK): the rejection propagates so the UI can show it. [Task 4]

## File Structure

| File | Responsibility |
|------|----------------|
| `backend/requirements.txt` (modify) | add `httpx2` |
| `backend/app/services/productservice.py` (modify) | strip whitespace in `search_products` |
| `backend/tests/test_api.py` (create) | HTTP-level tests for all endpoints plus CORS |
| `frontend/package.json` (modify) | dev dependencies and `test` script |
| `frontend/vite.config.ts` (modify) | `test` block: jsdom, setup file, env |
| `frontend/src/setupTests.ts` (create) | jest-dom matchers and per-test cleanup |
| `frontend/src/components/sentimentsummary.test.tsx` (create) | rounding tests |
| `frontend/src/components/productsearch.test.tsx` (create) | search UI behavior tests |
| `frontend/src/api/products.test.ts` (create) | API client tests with mocked `fetch` |
| `.github/workflows/ci.yml` (create) | the two CI jobs |
| `README.md`, `CLAUDE.md`, `docs/plan.md` (modify) | badge, commands, ticked items |

---

### Task 1: Backend API tests

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/services/productservice.py`
- Create: `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `app.main.app` (FastAPI instance), `app.data.products.products` (dict keyed by product id), `app.schemas.product.Product`.
- Produces: nothing later tasks depend on, except that `pytest` passes from `backend/` (Task 5 runs it in CI).

All commands run from `backend/` with the venv active (`. .venv/bin/activate`; recreate with `python3.13 -m venv .venv && pip install -r requirements.txt` if missing).

- [ ] **Step 1: Add the dependency**

Append one line to `backend/requirements.txt` so the file reads:

```text
fastapi==0.141.1
uvicorn==0.52.4
pydantic==2.13.5
pytest==9.1.1
httpx2==2.13.1
```

Run: `pip install -r requirements.txt`
Expected: installs `httpx2`; no errors.

- [ ] **Step 2: Write the failing tests**

Create `backend/tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient

from app.data.products import products
from app.main import app
from app.schemas.product import Product

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_without_query_returns_empty_list():
    assert client.get("/products").json() == []
    assert client.get("/products", params={"query": ""}).json() == []


def test_search_matches_partial_case_insensitive():
    response = client.get("/products", params={"query": "AIRPODS"})

    assert response.status_code == 200
    assert response.json() == [{"id": "airpods-pro", "name": "AirPods Pro"}]


def test_search_with_no_match_returns_empty_list():
    response = client.get("/products", params={"query": "zzz"})

    assert response.status_code == 200
    assert response.json() == []


def test_search_whitespace_only_returns_empty_list():
    response = client.get("/products", params={"query": "   "})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("query", ["(", "a&b", "%", ".*", "\\"])
def test_search_special_characters_do_not_error(query):
    response = client.get("/products", params={"query": query})

    assert response.status_code == 200
    assert response.json() == []


def test_get_product():
    response = client.get("/products/airpods-pro")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "airpods-pro"
    assert Product(**body).name == "AirPods Pro"


@pytest.mark.parametrize("product_id", list(products))
def test_every_fixture_product_is_served(product_id):
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert Product(**response.json()).id == product_id


def test_unknown_product_returns_404():
    response = client.get("/products/nope")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


@pytest.mark.parametrize("product_id", ["..%2Fetc", "a" * 5000, "%20"])
def test_odd_product_ids_return_404(product_id):
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_cors_allows_local_frontend_origin():
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_does_not_allow_unknown_origin():
    response = client.get("/health", headers={"Origin": "https://evil.example"})

    assert "access-control-allow-origin" not in response.headers
```

- [ ] **Step 3: Run the tests and confirm the expected failure**

Run: `python -m pytest tests/test_api.py -v`
Expected: all pass except `test_search_whitespace_only_returns_empty_list`, which fails because `["AirPods Pro", "Sony WH-1000XM6", "Steam Deck OLED"]` all match `" "`. If any other test fails, stop and investigate before continuing (for example, if an odd-id test returns a 404 with a different body, the router's path handling differs from what this plan assumes).

- [ ] **Step 4: Fix `search_products` to ignore surrounding whitespace**

In `backend/app/services/productservice.py`, replace the top of `search_products`:

```python
def search_products(query: str):
    if not query:
        return []

    query = query.lower()
```

with:

```python
def search_products(query: str):
    query = query.strip().lower()

    if not query:
        return []
```

- [ ] **Step 5: Run the whole backend suite**

Run: `python -m pytest -q`
Expected: all tests pass (the 13 existing plus the new ones).

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/app/services/productservice.py backend/tests/test_api.py
git commit -m "Add API tests and ignore whitespace-only product searches" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 2: Frontend test tooling and SentimentSummary tests

**Files:**
- Modify: `frontend/package.json` (via npm)
- Modify: `frontend/vite.config.ts`
- Create: `frontend/src/setupTests.ts`
- Create: `frontend/src/components/sentimentsummary.test.tsx`

**Interfaces:**
- Consumes: `SentimentSummary` default export from `frontend/src/components/sentimentsummary.tsx`. Props: `{ positive: number; neutral: number; negative: number }` (fractions, rendered as `Math.round(value * 100) + "%"`). The markup has three `<div class="sentiment-card">`, each containing a `<span>` label ("Positive", "Neutral", "Negative") and a `<strong>` value.
- Produces: `npm test` (`vitest run`) works; jest-dom matchers are available in every test; `import.meta.env.VITE_API_URL` is `http://api.test` during tests (Task 4 relies on this).

All commands run from `frontend/`.

- [ ] **Step 1: Install the test dependencies**

Run:
```bash
npm install -D vitest jsdom @testing-library/react @testing-library/dom @testing-library/user-event @testing-library/jest-dom
```
Expected: `package.json` and `package-lock.json` updated. `@testing-library/dom` is included because `@testing-library/react` lists it as a peer dependency.

- [ ] **Step 2: Add the test script**

In `frontend/package.json`, add `"test": "vitest run"` to `scripts`, after `"lint"`:

```json
    "lint": "eslint .",
    "test": "vitest run",
    "preview": "vite preview"
```

- [ ] **Step 3: Configure Vitest**

Replace `frontend/vite.config.ts` with:

```ts
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    env: {
      VITE_API_URL: 'http://api.test',
    },
  },
})
```

- [ ] **Step 4: Create the setup file**

Create `frontend/src/setupTests.ts`:

```ts
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
})
```

Cleanup is explicit because Testing Library only auto-registers it when test globals are enabled, and this config doesn't enable them.

- [ ] **Step 5: Write the SentimentSummary tests**

Create `frontend/src/components/sentimentsummary.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import SentimentSummary from "./sentimentsummary";

function renderSummary(positive: number, neutral: number, negative: number) {
  render(
    <SentimentSummary
      positive={positive}
      neutral={neutral}
      negative={negative}
    />,
  );
}

function cardFor(label: string) {
  return screen.getByText(label).parentElement;
}

describe("SentimentSummary", () => {
  it("renders each fraction as a whole percentage", () => {
    renderSummary(0.71, 0.18, 0.11);

    expect(cardFor("Positive")).toHaveTextContent("71%");
    expect(cardFor("Neutral")).toHaveTextContent("18%");
    expect(cardFor("Negative")).toHaveTextContent("11%");
  });

  it("rounds to the nearest whole percentage", () => {
    renderSummary(0.714, 0.716, 0);

    expect(cardFor("Positive")).toHaveTextContent("71%");
    expect(cardFor("Neutral")).toHaveTextContent("72%");
  });

  it("handles the extremes 0 and 1", () => {
    renderSummary(1, 0, 0);

    expect(cardFor("Positive")).toHaveTextContent("100%");
    expect(cardFor("Neutral")).toHaveTextContent("0%");
  });
});
```

- [ ] **Step 6: Run the tests, lint and build**

Run: `npm test`
Expected: 3 tests pass.

Run: `npm run lint && npm run build`
Expected: both exit 0. If `tsc -b` complains about `toHaveTextContent`, confirm `src/setupTests.ts` is inside `src/` (it is covered by `tsconfig.app.json`'s `include`) and that it imports `@testing-library/jest-dom/vitest`.

- [ ] **Step 7: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/src/setupTests.ts frontend/src/components/sentimentsummary.test.tsx
git commit -m "Add Vitest tooling and SentimentSummary tests" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 3: ProductSearch tests

**Files:**
- Create: `frontend/src/components/productsearch.test.tsx`

**Interfaces:**
- Consumes: `ProductSearch` default export from `./productsearch`, props `{ onSelectProduct: (productId: string) => void }`. It renders an `<input placeholder="Search for a product...">` and a `<button>Search</button>`. Clicking Search calls `searchProducts(query)` from `../api/products` (returns `Promise<ProductSearchResult[]>`, `ProductSearchResult = { id: string; name: string }`). Results render as a `<ul>` of buttons labelled with each name. An error shows its `message` in a `<p class="error-message">`. It does nothing for an empty or whitespace-only query. Selecting a result calls `onSelectProduct(id)`, clears the input and hides the list. The error state is reset to `""` at the start of each search.
- Produces: nothing later tasks use.

- [ ] **Step 1: Write the tests**

Create `frontend/src/components/productsearch.test.tsx`:

```tsx
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
```

- [ ] **Step 2: Run the tests**

Run (from `frontend/`): `npm test -- src/components/productsearch.test.tsx`
Expected: 7 tests pass (the `it.each` expands to two). These test existing behavior, so there is no red phase. To confirm the tests can fail, temporarily change `setError("")` in `productsearch.tsx` to a no-op comment, re-run, expect "clears an earlier error..." to fail, then revert the change with `git checkout frontend/src/components/productsearch.tsx`.

- [ ] **Step 3: Run lint and build**

Run: `npm run lint && npm run build`
Expected: both exit 0.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/productsearch.test.tsx
git commit -m "Add ProductSearch component tests" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 4: API client tests

**Files:**
- Create: `frontend/src/api/products.test.ts`

**Interfaces:**
- Consumes: `getProduct(productId: string): Promise<Product>` and `searchProducts(query: string): Promise<ProductSearchResult[]>` from `./products`. They call `fetch` with `${import.meta.env.VITE_API_URL}/products/${productId}` and `${VITE_API_URL}/products?query=${encodeURIComponent(query)}`, and throw `new Error("Failed to load product")` and `new Error("Failed to search products")` when `response.ok` is false. `VITE_API_URL` is `http://api.test` in tests (set in Task 2's `vite.config.ts`).
- Produces: nothing later tasks use.

- [ ] **Step 1: Write the tests**

Create `frontend/src/api/products.test.ts`:

```ts
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
```

- [ ] **Step 2: Run the whole frontend suite, lint and build**

Run: `npm test && npm run lint && npm run build`
Expected: all tests pass (3 + 7 + 6) and lint and build exit 0. If a URL assertion fails with `undefined/products/...`, `test.env` in `vite.config.ts` isn't being applied; re-check Task 2 Step 3.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api/products.test.ts
git commit -m "Add API client tests" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 5: CI workflow, README badge and docs

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md` (badge only)
- Modify: `CLAUDE.md` (commands and gotchas)
- Modify: `docs/plan.md` (tick two 0.2.1 items)

**Interfaces:**
- Consumes: `pytest` (from `backend/`) and `npm run lint`, `npm run build`, `npm test` (from `frontend/`), all passing locally after Tasks 1 to 4.
- Produces: the `CI` workflow, with jobs named `backend` and `frontend`.

`README.md` and `CLAUDE.md` have uncommitted edits from other work. Make only the changes below, and in the commit step stage them with `git add -p` so unrelated hunks are left out.

- [ ] **Step 1: Create the workflow**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: pip
          cache-dependency-path: backend/requirements.txt
      - run: pip install -r requirements.txt
      - run: pytest

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run build
        env:
          VITE_API_URL: http://localhost:8000
      - run: npm test
```

- [ ] **Step 2: Validate the YAML parses**

Run (from the repo root): `ruby -ryaml -e 'puts YAML.load_file(".github/workflows/ci.yml")["jobs"].keys.inspect'`
Expected: `["backend", "frontend"]`.

- [ ] **Step 3: Reproduce the CI steps locally from clean installs**

Run:
```bash
cd backend && rm -rf .venv && python3.13 -m venv .venv && . .venv/bin/activate && pip install -q -r requirements.txt && pytest -q && deactivate && cd ..
cd frontend && rm -rf node_modules && npm ci --silent && npm run lint && VITE_API_URL=http://localhost:8000 npm run build && npm test && cd ..
```
Expected: every command exits 0. This matches what the runners do, apart from the Node version (local Node may be newer than 22).

- [ ] **Step 4: Add the badge to the README**

In `README.md`, insert directly under the `# Product Sentiment Analyzer` heading, followed by a blank line:

```markdown
[![CI](https://github.com/bmshin02/Product-Sentiment-Analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/bmshin02/Product-Sentiment-Analyzer/actions/workflows/ci.yml)
```

- [ ] **Step 5: Update `CLAUDE.md`**

- In the frontend commands block, add `npm test` after `npm run lint`.
- Replace the Gotchas bullet that starts "There is no CI configured and no API tests yet" with:
  `- CI (`.github/workflows/ci.yml`) runs `pytest` and the frontend lint, build and test on every PR and push to `main`. Backend API tests use `TestClient`, which needs `httpx2` (not `httpx`). Frontend tests are Vitest and Testing Library, colocated as `*.test.ts(x)` next to the code.`

- [ ] **Step 6: Tick the plan items**

In `docs/plan.md`, change `- [ ]` to `- [x]` on the two 0.2.1 lines starting "Add API tests with FastAPI's `TestClient`" and "Add GitHub Actions CI".

- [ ] **Step 7: Commit**

```bash
git add .github/workflows/ci.yml docs/plan.md
git add -p README.md CLAUDE.md   # accept only the hunks from steps 4 and 5
git commit -m "Add GitHub Actions CI" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
git status --short
```
Expected: the leftover uncommitted files are only the unrelated ones (Docker files and other people's hunks of `README.md`/`CLAUDE.md`).

- [ ] **Step 8: Verify on GitHub (after the user pushes)**

Do not push without asking. Once the user pushes `ci-and-tests` and opens a PR, check that both `backend` and `frontend` jobs are green (`gh pr checks` or the Actions tab). If `frontend` fails only on Node 22 versus the local version, fix the cause rather than changing the Node version.

---

## Self-Review Notes

- **Spec coverage:** workflow and triggers (Task 5), all eight listed API cases plus the parametrized fixture check (Task 1), the Vitest dependencies, config and script (Task 2), the `SentimentSummary`, `ProductSearch` and API client tests (Tasks 2 to 4), README badge (Task 5), local and CI verification (Tasks 4 and 5).
- **Deviations from the spec, to flag when reporting:** `httpx2` instead of `httpx`; the whitespace fix to `search_products`; tick items and `CLAUDE.md` updates in Task 5.
- **Names used across tasks:** `searchProducts`, `getProduct`, `SentimentSummary`, `ProductSearch`, `VITE_API_URL=http://api.test` all match their definitions.
