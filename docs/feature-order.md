# Feature Order and Workflow

The order in which features get built. Each one goes through the Superpowers workflow below, so every feature has a written spec and plan before any code.

## Workflow (per feature)

1. **Spec**: `superpowers:brainstorming`. Settle goals, scope and design. Save the spec to `docs/specs/<feature>.md`.
2. **Plan**: `superpowers:writing-plans`. Break the spec into small tasks. Save the plan to `docs/plans/<feature>.md`.
3. **Isolate**: `superpowers:using-git-worktrees`. One branch or worktree per feature.
4. **Implement**: `superpowers:subagent-driven-development` (or `superpowers:executing-plans` for inline work), using `superpowers:test-driven-development` throughout.
5. **Debug**: `superpowers:systematic-debugging` when a test fails or behavior is unexpected.
6. **Verify**: `superpowers:verification-before-completion`. Run the tests, lint and build, and confirm the output before claiming it works.
7. **Review**: `superpowers:requesting-code-review`, then `superpowers:receiving-code-review` for the feedback.
8. **Merge**: `superpowers:finishing-a-development-branch`.

Update the README roadmap and `CLAUDE.md` when a feature changes commands or architecture.

## Order

| # | Feature | Roadmap | Why here |
|---|---------|---------|----------|
| 0 | Cleanup: UTF-8 `requirements.txt`, contraction handling, `id` on `Product`, more fixture comments | 0.2.1 | Removes known problems before building on them |
| 1 | CI/CD and API tests: GitHub Actions (pytest, lint, build), `TestClient` tests, Vitest setup | 0.2.1 | Every later feature gets checked automatically |
| 2 | Evaluated sentiment: hand-labeled set, VADER vs. lexicon vs. transformer, F1 and confusion matrix | 0.3 | Measure before adding more ML |
| 3 | Reddit ingestion pipeline: PRAW, Postgres, scheduled job, idempotent and deduplicated | 0.5 | Real data for everything after it |
| 4 | Aspect-based sentiment: computed positives and complaints per aspect | 0.4 | Replaces the hardcoded fixtures, so it needs real data from step 3 |
| 5 | Embeddings, semantic search and RAG with citations, plus retrieval evals | 0.6, 0.9 | Builds on stored comments |
| 6 | Clustering and topic discovery: HDBSCAN/BERTopic, UMAP plot | 0.7 | Reuses the embeddings |
| 7 | Time-series sentiment trends | n/a | Needs timestamps stored in step 3 |

## After the core

Pick these up in any order once the core is done:

- Product comparison view
- Spam and bot filtering
- Confidence intervals and sample-size warnings
- Observability and caching
- Docker and Alembic migrations
- Auth and rate limiting
- Streaming LLM summaries
- Model card and architecture doc

## Notes

- The architecture rule from `docs/plan.md` still applies: heavy work runs in the offline pipeline, and the API only reads precomputed results (Render free tier, 512MB).
- Step 2 sets the evaluation habit. Steps 4 and 5 should also report measured results, not just working demos.
