# Sentiment Scoring and Evaluation Design

Sub-project 2a of the 0.3 roadmap item (step 2 in `docs/feature-order.md`). Sub-project 2b (serving sentiment through the API and UI) is a separate spec.

## Goal

Build sentiment scorers and an evaluation harness that compares them against a hand-labeled dataset, then publish an honest written report. The deliverable is a measured answer to "which scorer should production use, and is a heavier model worth its cost?"

## Scope

- Production scorers: a VADER-based scorer and a hand-built lexicon scorer
- A transformer scorer, evaluated offline only
- A hand-labeled dataset of the 50 existing fixture comments, in a format that later accepts real Reddit comments
- Evaluation metrics, a command-line harness, and a generated report

Out of scope: API endpoints, frontend changes, `insightservice` (all 2b), aspect extraction, and training or fine-tuning models.

## Labels

Three classes: `positive`, `neutral`, `negative`. A comment that praises one thing and criticizes another with no clear net lean is `neutral`.

## Production code: `backend/app/services/analysis/`

**`sentiment.py`**
- `SentimentResult`: a small dataclass with `label: str` and `score: float`.
- `score_comment(text: str) -> SentimentResult`: VADER compound score. Labels use VADER's standard thresholds: `>= 0.05` is positive, `<= -0.05` is negative, otherwise neutral.
- `aggregate_sentiment(texts: list[str]) -> Sentiment`: fractions of positive, neutral and negative comments, using the existing `Sentiment` schema. An empty list returns all zeros.
- Adds `vaderSentiment` to `backend/requirements.txt`.

**`lexicon.py`**
- `score_comment(text: str) -> SentimentResult`, same signature as the VADER scorer.
- Uses `tokenize` from `textcleaner.py` (so contractions are already expanded and negation is explicit). It sums word polarities from a small hand-built lexicon (about 100 to 200 words in a module-level dict), flips the polarity of a word within a short window after a negation word (`not`, `no`, `never`), and scales it for intensifiers (`very`, `really`, `extremely`).
- Unknown words contribute zero. The label thresholds match the VADER scorer's.

## Evaluation code: `backend/eval/` (not part of the app)

- `data/labeled_comments.json`: a list of `{id, product_id, text, label, source}`. `source` is `fixture` now and `reddit` later. Ids are unique.
- `metrics.py`: accuracy, per-class precision, recall and F1, macro-F1, and the confusion matrix. Hand-written, with no scikit-learn dependency. A class with no predictions or no examples reports 0.0, not an error.
- `scorers.py`: a registry mapping a name to a scorer function with the signature `text -> SentimentResult`. Entries: `vader`, `lexicon`, `transformer`. The transformer is `cardiffnlp/twitter-roberta-base-sentiment-latest`, imported lazily so nothing heavy loads unless it is selected.
- `evaluate.py`: `python -m eval.evaluate [--scorers vader,lexicon,transformer]` loads the dataset, runs each chosen scorer, prints the metrics, and writes `docs/sentiment-evaluation.md`. The report includes per-scorer metrics, confusion matrices, a section of misclassified examples for error analysis, the dataset size and source breakdown, the transformer model name, and the run date.
- `requirements-eval.txt`: `transformers` and `torch`. CI and the deployed backend never install it.

## Label review gate

I draft the 50 labels. The author reviews and corrects them before any evaluation numbers are generated or reported. The report must not be generated from unreviewed labels.

## Honesty rules for the report

- The first numbers come from 50 fixture comments written for this project. They are cleaner than real Reddit text, so scores will be optimistic. The report says so and notes it will be re-run on real comments after Reddit ingestion (step 3).
- Thresholds stay at VADER's defaults. Tuning them on the same 50 comments would overfit.
- The report shows per-class results, not only accuracy, because neutral is where scorers usually fail.
- The transformer's numbers come from a local run, and the report records which model and date.

## Testing (runs in CI, no transformer)

- `metrics.py` against hand-computed values on tiny inputs, including empty classes.
- The VADER scorer: threshold edges (0.05 and -0.05), that "isn't terrible" is not labeled negative, and `aggregate_sentiment` on an empty list and on mixed input.
- The lexicon scorer: negation flips polarity, intensifiers scale it, and unknown words give neutral.
- Dataset validation: ids are unique, labels are valid, and every comment in `app/data/comments.py` appears exactly once with its product id.
- The harness run end to end with a stub scorer, checking that the report file is written with the expected sections.

## Verification

- `pytest` passes in `backend/`, and the new tests run in the existing CI workflow unchanged.
- `python -m eval.evaluate --scorers vader,lexicon` runs locally and writes a report after labels are reviewed.
- The transformer run is done once locally with the eval requirements installed, and its results are committed in the report.
