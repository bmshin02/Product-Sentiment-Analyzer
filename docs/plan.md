# Roadmap

This roadmap takes Product Sentiment Analyzer from fixture data (0.2) to a Reddit-backed product research tool with AI summaries and semantic search (1.0).

## Where things stand (0.2)

- The dashboard works end to end, but every value it shows is hardcoded in `backend/app/data/products.py`.
- `backend/app/data/comments.py` holds sample comments for 2 of the 3 products, and nothing reads it yet.
- The NLP utilities in `backend/app/services/analysis/` (cleaning, tokenizing, stop words, word frequencies, n-grams) are tested but not wired into the API.

## Architecture: analyze offline, serve precomputed results

Render's free tier has 512MB of RAM and sleeps when idle. ML models won't fit there, and fetching from Reddit is too slow to run per request. So heavy work runs in a separate pipeline, and the API only reads its results:

```text
[pipeline: CLI / scheduled job]              [API: FastAPI on Render]
Reddit → clean → sentiment → aspects →  DB  ← reads precomputed results
         embeddings → clusters → summary
```

Data ingestion (0.5) comes before embeddings and clustering (0.6–0.7), so those steps get built and evaluated on real data rather than a handful of fixture comments.

---

## 0.2.1: Cleanup

- [x] Re-save `backend/requirements.txt` as UTF-8 (it's currently UTF-16 from PowerShell's `pip freeze >`) and trim it to direct dependencies
- [x] Expand contractions in `clean_text` before stripping punctuation, so "isn't" becomes "is not" rather than `isnt` and the negation survives. Add tests
- [x] Add `id` to the `Product` schema
- [x] Add fixture comments for `steam-deck-oled` and grow every product to about 15–20 comments
- [x] Add API tests with FastAPI's `TestClient` (`backend/tests/test_api.py`)
- [x] Add GitHub Actions CI: backend `pytest`, frontend `npm run lint && npm run build`
- [x] README: macOS/Linux setup commands, and an accurate project structure
- [x] Make the app title consistent ("Reddit Product Intelligence" in `App.tsx` vs. "Product Sentiment Analyzer")

## 0.3: Sentiment analysis

- [ ] `services/analysis/sentiment.py` with `score_comment(text)` → label + compound score, and `aggregate_sentiment(texts)` → `Sentiment`
- [ ] Use VADER (`vaderSentiment`): lightweight, tuned for social media, handles negation, caps and "!!!"
- [ ] Optional: a hand-built lexicon scorer to compare against VADER
- [ ] Hand-labeled evaluation set (`backend/tests/fixtures/labeled_comments.json`) and an accuracy report
- [ ] `services/insightservice.py` builds a `Product` from comments (computed sentiment, `reviews_analyzed = len(comments)`)
- [ ] `GET /products/{id}/comments`: each comment with its sentiment label
- [ ] Frontend: sentiment bar, and a sample-comments list colored by sentiment

## 0.4: Aspect / topic extraction

- [ ] Find candidate aspects ("battery life", "noise cancellation") with `get_top_ngrams` from `textstats.py`
- [ ] Aspect-based sentiment: score the sentences that mention each aspect. Positive ones go to `top_positives`, negative ones to `top_complaints`
- [ ] Alias map to merge synonyms ("noise cancelling" → "noise cancellation")
- [ ] Schema: insights become `{label, mentions, sentiment}` instead of `str`
- [ ] Frontend: mention counts on each insight, and clicking an insight shows its supporting comments

## 0.5: Reddit ingestion + PostgreSQL

- [ ] Confirm Reddit API access and terms before building (register an app, check your use case is allowed and note the rate limits), then use PRAW
- [ ] Postgres (Neon, Supabase or Render) with SQLAlchemy 2.0 and Alembic
- [ ] Tables: `products`, `posts`, `comments`, `comment_sentiment`, `product_insights`
- [ ] Pipeline CLI `backend/pipeline/run.py <product>`: fetch → filter (relevance, length, dedupe) → analyze → store
- [ ] Move `productservice.py` from fixture dicts to DB queries, keeping the API contracts unchanged
- [ ] Scheduled runs (GitHub Actions cron or Render cron)
- [ ] Frontend: "last updated" timestamp and links to the source threads

## 0.6: Semantic embeddings

- [ ] Embed comments in the pipeline (`all-MiniLM-L6-v2` or a hosted embedding API), never inside the API server
- [ ] Store vectors in Postgres with pgvector
- [ ] Replace the 0.4 alias map with embedding similarity to merge aspects

## 0.7: Comment clustering

- [ ] Cluster embeddings (start with KMeans, then UMAP + HDBSCAN or BERTopic)
- [ ] Label clusters with their top n-grams and store them per product
- [ ] Frontend: "Themes" section with cluster size, sentiment and example comments

## 0.8: AI summaries

- [ ] In the pipeline, send clusters, aspect stats and representative comments to an LLM (e.g. the Claude API) and store a product summary plus pros and cons
- [ ] Ground claims in retrieved comments and cite comment IDs
- [ ] Frontend: summary card at the top of the dashboard

## 0.9: Semantic search / RAG

- [ ] `POST /products/{id}/ask`: pgvector similarity search, then an LLM answer with cited comments
- [ ] Rate limiting and response caching on the public endpoint

## 1.0: Production polish

- [ ] Request a new product, which queues a pipeline run
- [ ] Side-by-side product comparison
- [ ] Sentiment over time
- [ ] Structured logging, error tracking and pipeline run history
- [ ] Architecture diagram and an evaluation write-up
