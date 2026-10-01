# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Full-stack product sentiment dashboard: a FastAPI backend (`backend/`) and a React + TypeScript + Vite frontend (`frontend/`). Currently at v0.2. The API serves **hardcoded fixture data**, and the NLP utilities are tested but not yet wired into any endpoint. `docs/plan.md` holds the roadmap (planned: VADER sentiment, Reddit ingestion, PostgreSQL/pgvector, embeddings, RAG). The planned architecture is to analyze offline in a separate pipeline and have the API read precomputed results, because Render's free tier (512MB, sleeps when idle) can't run ML models per request.

## Commands

Backend (run from `backend/`; the app imports as `app.*`, so run everything from that directory):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload          # http://localhost:8000, docs at /docs
pytest                                 # all tests
pytest tests/test_textanalysis.py::test_clean_text   # single test
```

Frontend (run from `frontend/`; needs `frontend/.env` with `VITE_API_URL=http://localhost:8000`, see `.env.example`):

```bash
npm install
npm run dev
npm run lint
npm test
npm run build      # tsc -b && vite build
```

## Architecture

- **Backend layering:** `api/routes/*` (thin FastAPI routers) → `services/productservice.py` (search/lookup logic) → `data/products.py` (fixture dict keyed by product id, e.g. `airpods-pro`). `schemas/product.py` holds the Pydantic response models. Routers are registered in `app/main.py`, which also hardcodes the CORS allowed origins (localhost:5173 and the Vercel deployment); update it if the frontend origin changes.
- **NLP pipeline (`services/analysis/`):** `textcleaner.py` (clean → tokenize → stop-word removal, with `stopwords.py`) feeds `textstats.py` (word and n-gram frequencies). Input comes from `data/comments.py` (sample comments per product id), which nothing consumes yet.
- **Frontend:** `App.tsx` composes components in `src/components/`; all HTTP goes through `src/api/products.ts`, which reads `VITE_API_URL`. Types in `src/types/product.ts` mirror the backend Pydantic schemas, so change both together.
- **Deployment:** frontend on Vercel, backend on Render (free tier, so cold starts are slow).

## Gotchas

- CI (`.github/workflows/ci.yml`) runs `pytest` and the frontend lint, build and test on every PR and push to `main`. Backend API tests use `TestClient`, which needs `httpx2` (not `httpx`). Frontend tests are Vitest and Testing Library, colocated as `*.test.ts(x)` next to the code.
