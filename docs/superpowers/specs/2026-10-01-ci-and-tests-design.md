# CI and Tests Design

Step 1 of `docs/feature-order.md`. Adds automated checks so every later feature is verified on each push.

## Goal

Catch regressions automatically on both sides of the app. Deployment stays as it is today (Vercel and Render); CI only checks code.

## Scope

- GitHub Actions workflow running backend and frontend checks
- `TestClient` API tests for the existing endpoints
- Vitest and Testing Library for the frontend, with a first set of tests
- CI status badge in the README

Out of scope: deployment steps, coverage thresholds, branch protection rules (a GitHub setting), Dependabot, tests for `App.tsx` (it will change in 0.3).

## CI workflow

File: `.github/workflows/ci.yml`. One workflow with two parallel jobs.

- **Triggers:** `pull_request`, and `push` to `main`. In-progress runs for the same ref are cancelled.
- **`backend` job:** Python 3.13, pip cache keyed on `backend/requirements.txt`, then `pip install -r requirements.txt` and `pytest`, with `working-directory: backend`.
- **`frontend` job:** Node 22, `npm ci` with the npm cache, then `npm run lint`, `npm run build` and `npm test`, with `working-directory: frontend`. `VITE_API_URL` is set to a dummy value for the build.

Rejected alternatives: separate workflows with path filters (skipped workflows leave required checks pending) and one sequential job (a backend failure hides frontend results).

## Backend API tests

File: `backend/tests/test_api.py`. Uses FastAPI's `TestClient`, so tests run in-process with no network. `httpx` is added to `backend/requirements.txt` because `TestClient` needs it.

Cases:

- `GET /health` returns 200 and `{"status": "ok"}`
- `GET /products` with an empty or missing query returns `[]`
- A partial, case-insensitive query returns matches containing `id` and `name`
- A query with no matches returns `[]`
- `GET /products/airpods-pro` returns 200 with a payload that validates against `Product` and includes `id`
- `GET /products/nope` returns 404 with `{"detail": "Product not found"}`
- CORS: a request with `Origin: http://localhost:5173` gets a matching `access-control-allow-origin` header
- Parametrized over every fixture product id: `GET /products/{id}` returns 200 and a valid `Product`

## Frontend tests

Dev dependencies: `vitest`, `jsdom`, `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom`.

- `vite.config.ts` gets a `test` block (jsdom environment, setup file that loads jest-dom matchers).
- `package.json` gets `"test": "vitest run"`.
- Test files must pass `npm run lint` and `tsc -b`, without breaking `npm run build`.

Tests:

- `SentimentSummary`: 0.71 renders as "71%"; fractional values round as `Math.round` does
- `ProductSearch`: typing then clicking Search lists results; clicking a result calls `onSelectProduct` with its id and clears the input and list; an empty or whitespace query lists nothing; a failed request shows the error message
- `api/products.ts`: requests the correct URLs, encodes the query with `encodeURIComponent`, and throws on a non-OK response. `fetch` is mocked.

## README

Add a CI status badge for the workflow near the top.

## Verification

- Locally: `pytest` in `backend/`, and `npm run lint`, `npm run build`, `npm test` in `frontend/`, all passing.
- After the branch is pushed: the first Actions run is green on both jobs.
