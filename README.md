# Product Sentiment Analyzer

Product Sentiment Analyzer is a full-stack product research application designed to transform consumer discussions into structured product insights.

The project is being built incrementally to explore **natural language processing, machine learning, and full-stack development**. The long-term goal is to analyze Reddit discussions for sentiment, common complaints, praised features, and recurring product topics.

## Live Demo

NOTE: Backend is using Render on free plan so please wait for it to load for data to show up. 

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

- Sentiment analysis (VADER)
- Aspect-based sentiment
- Reddit API integration
- PostgreSQL + pgvector
- Semantic embeddings
- Topic clustering
- AI summaries / RAG

## Project Structure

```text
Product-Sentiment-Analyzer/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # FastAPI routers
│   │   ├── data/            # fixture products and comments
│   │   ├── schemas/         # Pydantic models
│   │   └── services/        # product service + NLP analysis
│   └── tests/
├── frontend/
│   └── src/                 # components, API client, types
├── docs/                    # roadmap and planning notes
└── README.md
```

## Local Development

### Backend

macOS / Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Windows (PowerShell):

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run the tests with `pytest` from `backend/`.

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
- 0.4 — Aspect / topic extraction
- 0.5 — Reddit ingestion + PostgreSQL
- 0.6 — Semantic embeddings
- 0.7 — Comment clustering
- 0.8 — AI summaries
- 0.9 — Semantic search / RAG
- 1.0 — Production polish

See [docs/ROADMAP.md](docs/ROADMAP.md) for each milestone's tasks.
