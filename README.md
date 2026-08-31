# Reddit Product Intelligence

Reddit Product Intelligence is a full-stack product research application designed to transform consumer discussions into structured product insights.

The long-term goal is to analyze Reddit discussions using natural language processing, sentiment analysis, semantic embeddings, topic clustering, and evidence-grounded AI summaries.

## Current Version — 0.1

The current MVP uses fixture data to establish the application's full-stack architecture before integrating real Reddit data or machine learning.

Current features include:

- Product search
- Product sentiment summaries
- Top positive product attributes
- Common complaints
- React and FastAPI communication
- Loading and error states
- Validated FastAPI response schemas

## Tech Stack

### Frontend

- React
- TypeScript
- Vite

### Backend

- Python
- FastAPI
- Pydantic

### Planned

- PostgreSQL
- NLP sentiment analysis
- Semantic embeddings
- Topic clustering
- Reddit data ingestion
- Retrieval-augmented generation

## Project Structure

```text
reddit-product-intelligence/
├── frontend/
├── backend/
├── data/
├── docs/
└── README.md
```

## Local Development

### Backend

```bash
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at:

```text
http://localhost:8000
https://reddit-product-intelligence.onrender.com/
```

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

### Frontend

Create:

```text
frontend/.env
```

with:

```env
VITE_API_URL=http://localhost:8000
```

Then:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:5173
https://product-sentiment-analyzer-amber.vercel.app/
```

## Roadmap

- 0.1 — Product dashboard using fixture data
- 0.2 — Text cleaning and NLP fundamentals
- 0.3 — Sentiment analysis
- 0.4 — Topic extraction
- 0.5 — Semantic embeddings
- 0.6 — Comment clustering
- 0.7 — Reddit ingestion
- 0.8 — PostgreSQL integration
- 0.9 — AI-generated summaries
- 1.0 — Semantic search and RAG
- 1.1 — Product comparison
- 1.2 — AI evaluation suite
