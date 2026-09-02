# Product Sentiment Analyzer

Product Sentiment Analyzer is a full-stack product research application designed to transform consumer discussions into structured product insights.

The project is being built incrementally to explore **natural language processing, machine learning, and full-stack development**. The long-term goal is to analyze Reddit discussions for sentiment, common complaints, praised features, and recurring product topics.

## Live Demo

**Frontend:**  
https://product-sentiment-analyzer-amber.vercel.app/

**API:**  
https://reddit-product-intelligence.onrender.com/

**API Docs:**  
https://reddit-product-intelligence.onrender.com/docs

## Current Version — 0.2

The application currently uses fixture product data while the NLP pipeline is being developed.

### Features

- Product search
- Product sentiment dashboard
- Positive attributes and common complaints
- React frontend connected to FastAPI
- Loading and error handling
- Pydantic API validation
- Text cleaning and normalization
- Tokenization
- Stop-word filtering
- Word-frequency analysis
- N-gram analysis
- Unit tests with pytest

## Tech Stack

**Frontend**

- React
- TypeScript
- Vite
- Vercel

**Backend**

- Python
- FastAPI
- Pydantic
- pytest
- Render

**Planned**

- Sentiment analysis
- PostgreSQL
- Semantic embeddings
- Topic clustering
- Reddit API integration
- RAG / AI summaries

## Project Structure

```text
product-sentiment-analyzer/
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

### Frontend

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Then:

```bash
cd frontend
npm install
npm run dev
```

## Roadmap

- ✅ 0.1 — Full-stack product dashboard
- ✅ 0.2 — NLP text preprocessing
- 0.3 — Sentiment analysis
- 0.4 — Topic extraction
- 0.5 — Semantic embeddings
- 0.6 — Comment clustering
- 0.7 — Reddit ingestion
- 0.8 — PostgreSQL
- 0.9 — AI summaries
- 1.0 — Semantic search / RAG
- 1.1 — Product comparison
- 1.2 — Evaluation suite
