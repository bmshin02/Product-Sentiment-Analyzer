# Sentiment Scoring and Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add VADER and lexicon sentiment scorers, a hand-labeled dataset, an evaluation harness, and a published report comparing the scorers (and a transformer, run offline).

**Architecture:** Production scorers live in `backend/app/services/analysis/` and share one signature, `score_comment(text) -> SentimentResult`. Evaluation code lives in `backend/eval/`, outside the app, with a registry of scorers, hand-written metrics, and a CLI that writes `docs/sentiment-evaluation.md`. Heavy transformer dependencies live only in `requirements-eval.txt` and are imported lazily.

**Tech Stack:** Python 3.13, `vaderSentiment` 3.3.2, pytest; `transformers` and `torch` (eval only).

**Spec:** `docs/superpowers/specs/2026-10-01-sentiment-evaluation-design.md`

## Global Constraints

- Three labels only: `positive`, `neutral`, `negative`. Thresholds are VADER's defaults: score `>= 0.05` is positive, `<= -0.05` is negative, otherwise neutral. Thresholds are never tuned on the dataset.
- `vaderSentiment==3.3.2` goes in `backend/requirements.txt`; `transformers` and `torch` go only in `backend/requirements-eval.txt`. CI and the deployed backend never install the eval file, and nothing under `app/` may import them.
- No scikit-learn; metrics are hand-written.
- The report is never generated from unreviewed labels (see the gate in Task 6) and must state that fixture comments were written for this project, so scores are optimistic, and that the lexicon author had seen the fixtures.
- All commands run from `backend/` with the venv active (`. .venv/bin/activate`) unless stated.
- Stage files by exact path in every commit. The working tree has unrelated uncommitted files (Docker files, `README.md` and `CLAUDE.md` edits, a root `package-lock.json`); never use `git add -A` or `git add .`.
- **Never open a file in write mode before reading it.** An earlier edit script truncated `README.md` that way. Read the content into a variable first, then write.
- Commit messages end with:
  ```
  Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348
  ```

## Review Focus

Inputs the spec implies but its listed tests would not exercise. Each has a test in the task named in brackets.

1. **Blank or whitespace-only comment text** (`""`, `"   "`, `"\n\t"`): expect `neutral`, not an error. [Tasks 1 and 2]
2. **Emoji and non-ASCII text**: must not crash, and must return a valid label. [Tasks 1 and 2]
3. **A class with no predictions, no examples, or empty input** in the metrics: scores 0.0, never a ZeroDivisionError. [Task 3]
4. **`--output` pointing into a directory that does not exist yet** (for example a fresh checkout without `docs/`): the harness creates it. [Task 4]
5. **A mistyped scorer name on the command line**: a clean one-line error and exit code 2, not a traceback. [Task 4]
6. **Importing the scorer registry must not import `transformers` or `torch`**, so CI and the API stay light. [Task 4]

## File Structure

| File | Responsibility |
|------|----------------|
| `backend/requirements.txt` (modify) | add `vaderSentiment` |
| `backend/requirements-eval.txt` (create) | `transformers`, `torch` for the offline transformer run |
| `backend/app/services/analysis/sentiment.py` (create) | `SentimentResult`, `label_for_score`, VADER `score_comment`, `aggregate_sentiment` |
| `backend/app/services/analysis/lexicon.py` (create) | hand-built lexicon scorer with the same signature |
| `backend/eval/__init__.py` (create) | package marker |
| `backend/eval/metrics.py` (create) | confusion matrix, per-class and macro metrics |
| `backend/eval/scorers.py` (create) | scorer registry plus lazy transformer scorer |
| `backend/eval/evaluate.py` (create) | dataset loader, evaluation, report rendering, CLI |
| `backend/eval/data/labeled_comments.json` (create) | the 50 labeled fixture comments |
| `backend/tests/test_sentiment.py`, `test_lexicon.py`, `test_metrics.py`, `test_evaluate.py`, `test_labeled_dataset.py` (create) | tests for the above |
| `docs/sentiment-evaluation.md` (create, generated) | the published report |
| `CLAUDE.md`, `README.md`, `docs/plan.md` (modify) | commands, link, ticked items |

---

### Task 1: VADER scorer

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/services/analysis/sentiment.py`
- Test: `backend/tests/test_sentiment.py`

**Interfaces:**
- Consumes: `app.schemas.product.Sentiment` (fields `positive`, `neutral`, `negative`, all `float`).
- Produces: `SentimentResult(label: str, score: float)` (frozen dataclass); `label_for_score(score: float) -> str`; `score_comment(text: str) -> SentimentResult`; `aggregate_sentiment(texts: list[str]) -> Sentiment`; constants `POSITIVE_THRESHOLD = 0.05`, `NEGATIVE_THRESHOLD = -0.05`. Tasks 2, 4 import `SentimentResult` and `label_for_score` from here.

- [ ] **Step 1: Add the dependency**

Append `vaderSentiment==3.3.2` to `backend/requirements.txt` so it reads:

```text
fastapi==0.141.1
uvicorn==0.52.4
pydantic==2.13.5
pytest==9.1.1
httpx2==2.13.1
vaderSentiment==3.3.2
```

Run: `pip install -r requirements.txt`
Expected: installs `vaderSentiment` (and its `requests` dependency) without errors.

- [ ] **Step 2: Write the failing tests**

Create `backend/tests/test_sentiment.py`:

```python
import pytest

from app.services.analysis.sentiment import (
    aggregate_sentiment,
    label_for_score,
    score_comment,
)


@pytest.mark.parametrize(
    "score, label",
    [
        (0.05, "positive"),
        (0.0499, "neutral"),
        (0.0, "neutral"),
        (-0.0499, "neutral"),
        (-0.05, "negative"),
        (0.9, "positive"),
        (-0.9, "negative"),
    ],
)
def test_label_for_score_thresholds(score, label):
    assert label_for_score(score) == label


def test_score_comment_positive():
    result = score_comment("I love the transparency mode.")

    assert result.label == "positive"
    assert result.score > 0


def test_score_comment_negative():
    result = score_comment("The battery is terrible and I hate it.")

    assert result.label == "negative"
    assert result.score < 0


def test_score_comment_without_sentiment_is_neutral():
    result = score_comment("The box contains a cable.")

    assert result.label == "neutral"


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_score_comment_blank_text_is_neutral(text):
    assert score_comment(text).label == "neutral"


def test_score_comment_handles_emoji_and_non_ascii_text():
    result = score_comment("great \U0001f60d battery \u2014 tr\u00e8s bon")

    assert result.label in {"positive", "neutral", "negative"}


def test_negated_negative_is_not_labeled_negative():
    assert score_comment("The battery isn't terrible").label != "negative"


def test_aggregate_sentiment_empty_list_is_all_zero():
    result = aggregate_sentiment([])

    assert (result.positive, result.neutral, result.negative) == (0.0, 0.0, 0.0)


def test_aggregate_sentiment_mixed_input():
    result = aggregate_sentiment(
        ["I love it", "This is terrible", "The box contains a cable"]
    )

    assert result.positive == pytest.approx(1 / 3)
    assert result.neutral == pytest.approx(1 / 3)
    assert result.negative == pytest.approx(1 / 3)


def test_aggregate_sentiment_fractions_sum_to_one():
    result = aggregate_sentiment(["great", "good", "bad", "the box"])

    assert result.positive + result.neutral + result.negative == pytest.approx(1.0)
```

- [ ] **Step 3: Run the tests and confirm they fail**

Run: `python -m pytest tests/test_sentiment.py -q`
Expected: a collection error, `ModuleNotFoundError: No module named 'app.services.analysis.sentiment'`.

- [ ] **Step 4: Implement the scorer**

Create `backend/app/services/analysis/sentiment.py`:

```python
from dataclasses import dataclass

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.schemas.product import Sentiment

POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05

_analyzer = SentimentIntensityAnalyzer()


@dataclass(frozen=True)
class SentimentResult:
    label: str
    score: float


def label_for_score(score: float) -> str:
    if score >= POSITIVE_THRESHOLD:
        return "positive"

    if score <= NEGATIVE_THRESHOLD:
        return "negative"

    return "neutral"


def score_comment(text: str) -> SentimentResult:
    score = _analyzer.polarity_scores(text)["compound"]

    return SentimentResult(label=label_for_score(score), score=score)


def aggregate_sentiment(texts: list[str]) -> Sentiment:
    if not texts:
        return Sentiment(positive=0.0, neutral=0.0, negative=0.0)

    counts = {"positive": 0, "neutral": 0, "negative": 0}

    for text in texts:
        counts[score_comment(text).label] += 1

    total = len(texts)

    return Sentiment(
        positive=counts["positive"] / total,
        neutral=counts["neutral"] / total,
        negative=counts["negative"] / total,
    )
```

- [ ] **Step 5: Run the tests**

Run: `python -m pytest tests/test_sentiment.py -q`
Expected: 18 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/app/services/analysis/sentiment.py backend/tests/test_sentiment.py
git commit -m "Add VADER sentiment scorer" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 2: Lexicon scorer

**Files:**
- Create: `backend/app/services/analysis/lexicon.py`
- Test: `backend/tests/test_lexicon.py`

**Interfaces:**
- Consumes: `SentimentResult` and `label_for_score` from `app.services.analysis.sentiment` (Task 1); `tokenize(text) -> list[str]` from `app.services.analysis.textcleaner` (lowercases, expands contractions such as "isn't" to "is not", strips punctuation).
- Produces: `score_comment(text: str) -> SentimentResult` with the same signature as the VADER scorer; the score is normalized to the open interval (-1, 1) and labeled with the shared thresholds. Constants `LEXICON`, `NEGATORS`, `INTENSIFIERS`, `SCOPE_BREAKERS`. Task 4 registers `lexicon.score_comment` under the name `lexicon`.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_lexicon.py`:

```python
import pytest

from app.services.analysis.lexicon import score_comment


def test_positive_word_is_positive():
    assert score_comment("great battery").label == "positive"


def test_negative_word_is_negative():
    assert score_comment("terrible battery").label == "negative"


def test_unknown_words_are_neutral_with_zero_score():
    result = score_comment("the battery")

    assert result.label == "neutral"
    assert result.score == 0.0


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_blank_text_is_neutral(text):
    assert score_comment(text).label == "neutral"


def test_handles_emoji_and_non_ascii_text():
    result = score_comment("great \U0001f60d battery \u2014 tr\u00e8s bon")

    assert result.label == "positive"


def test_negation_flips_a_positive_word():
    assert score_comment("it isn't good").label == "negative"


def test_negation_flips_a_negative_word():
    assert score_comment("it is not terrible").label == "positive"


def test_negation_does_not_cross_a_but():
    assert score_comment("not good but great").label == "positive"


def test_intensifier_increases_magnitude():
    assert score_comment("really good").score > score_comment("good").score


def test_score_stays_within_unit_range():
    result = score_comment("amazing incredible excellent perfect love best")

    assert 0.9 < result.score < 1.0
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `python -m pytest tests/test_lexicon.py -q`
Expected: a collection error, `ModuleNotFoundError: No module named 'app.services.analysis.lexicon'`.

- [ ] **Step 3: Implement the scorer**

Create `backend/app/services/analysis/lexicon.py`. Keep the word list general-purpose product-review vocabulary; do not add or remove words after looking at evaluation results, which would contaminate the evaluation.

```python
import math

from app.services.analysis.sentiment import SentimentResult, label_for_score
from app.services.analysis.textcleaner import tokenize

LEXICON = {
    # strongly positive
    "amazing": 3, "amazingly": 3, "awesome": 3, "best": 3, "excellent": 3,
    "fantastic": 3, "flawless": 3, "flawlessly": 3, "gorgeous": 3,
    "incredible": 3, "love": 3, "loved": 3, "outstanding": 3, "perfect": 3,
    "stunning": 3,
    # positive
    "beautiful": 2, "bright": 2, "clear": 2, "comfortable": 2,
    "comfortably": 2, "convenient": 2, "crisp": 2, "enjoy": 2, "fast": 2,
    "good": 2, "great": 2, "happy": 2, "impressive": 2, "natural": 2,
    "nice": 2, "quiet": 2, "quieter": 2, "recommend": 2, "reliable": 2,
    "seamless": 2, "smooth": 2, "solid": 2, "sturdy": 2, "worth": 2,
    # mildly positive
    "better": 1, "decent": 1, "easy": 1, "fine": 1, "improved": 1,
    "pleasant": 1, "useful": 1,
    # strongly negative
    "awful": -3, "broken": -3, "disappointing": -3, "garbage": -3,
    "hate": -3, "hated": -3, "horrible": -3, "ridiculous": -3,
    "ridiculously": -3, "terrible": -3, "unusable": -3, "useless": -3,
    "worst": -3,
    # negative
    "annoying": -2, "bad": -2, "buggy": -2, "disappointed": -2, "dying": -2,
    "expensive": -2, "fails": -2, "flimsy": -2, "laggy": -2, "mediocre": -2,
    "noisy": -2, "overpriced": -2, "poor": -2, "slow": -2, "struggle": -2,
    "struggles": -2, "uncomfortable": -2, "worse": -2,
    # mildly negative
    "bulky": -1, "heavy": -1, "issue": -1, "issues": -1, "lack": -1,
    "limited": -1, "pricey": -1, "problem": -1, "tight": -1, "wish": -1,
}

NEGATORS = {"not", "no", "never", "cannot", "hardly"}
INTENSIFIERS = {
    "very", "really", "super", "extremely", "incredibly", "absolutely",
    "so", "too", "way",
}
SCOPE_BREAKERS = {"but", "however", "although"}

NEGATION_WINDOW = 3
NEGATION_FACTOR = -0.5
INTENSIFIER_FACTOR = 1.5
NORMALIZATION_ALPHA = 15


def _is_negated(tokens: list[str], index: int) -> bool:
    for previous in reversed(tokens[max(0, index - NEGATION_WINDOW):index]):
        if previous in SCOPE_BREAKERS:
            return False

        if previous in NEGATORS:
            return True

    return False


def _is_intensified(tokens: list[str], index: int) -> bool:
    return any(token in INTENSIFIERS for token in tokens[max(0, index - 2):index])


def score_comment(text: str) -> SentimentResult:
    tokens = tokenize(text)
    total = 0.0

    for index, token in enumerate(tokens):
        polarity = LEXICON.get(token)

        if polarity is None:
            continue

        value = float(polarity)

        if _is_intensified(tokens, index):
            value *= INTENSIFIER_FACTOR

        if _is_negated(tokens, index):
            value *= NEGATION_FACTOR

        total += value

    score = total / math.sqrt(total * total + NORMALIZATION_ALPHA)

    return SentimentResult(label=label_for_score(score), score=score)
```

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests/test_lexicon.py -q`
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/analysis/lexicon.py backend/tests/test_lexicon.py
git commit -m "Add hand-built lexicon sentiment scorer" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 3: Evaluation metrics

**Files:**
- Create: `backend/eval/__init__.py` (empty)
- Create: `backend/eval/metrics.py`
- Test: `backend/tests/test_metrics.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `LABELS = ["positive", "neutral", "negative"]` (matrix row and column order); `confusion_matrix(y_true, y_pred) -> list[list[int]]` (rows are true labels, columns are predictions; raises `ValueError` on mismatched lengths or an unknown label); `classification_report(y_true, y_pred) -> dict` with keys `accuracy`, `macro_f1`, `per_class` (label to `{precision, recall, f1, support}`), `confusion_matrix`. Tasks 4 and 5 use these.

- [ ] **Step 1: Write the failing tests**

Create an empty `backend/eval/__init__.py`, then create `backend/tests/test_metrics.py`:

```python
import pytest

from eval.metrics import LABELS, classification_report, confusion_matrix

Y_TRUE = ["positive", "positive", "negative", "neutral"]
Y_PRED = ["positive", "negative", "negative", "positive"]


def test_labels_order():
    assert LABELS == ["positive", "neutral", "negative"]


def test_confusion_matrix_rows_are_true_labels_columns_are_predictions():
    assert confusion_matrix(Y_TRUE, Y_PRED) == [
        [1, 0, 1],
        [1, 0, 0],
        [0, 0, 1],
    ]


def test_classification_report_matches_hand_computed_values():
    report = classification_report(Y_TRUE, Y_PRED)

    assert report["accuracy"] == pytest.approx(0.5)
    assert report["per_class"]["positive"] == pytest.approx(
        {"precision": 0.5, "recall": 0.5, "f1": 0.5, "support": 2}
    )
    assert report["per_class"]["negative"] == pytest.approx(
        {"precision": 0.5, "recall": 1.0, "f1": 2 / 3, "support": 1}
    )
    assert report["macro_f1"] == pytest.approx((0.5 + 0.0 + 2 / 3) / 3)


def test_class_with_no_predictions_scores_zero_not_an_error():
    report = classification_report(Y_TRUE, Y_PRED)

    assert report["per_class"]["neutral"] == {
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "support": 1,
    }


def test_class_with_no_examples_scores_zero_not_an_error():
    report = classification_report(["positive", "positive"], ["positive", "positive"])

    assert report["accuracy"] == 1.0
    assert report["per_class"]["negative"]["support"] == 0
    assert report["per_class"]["negative"]["f1"] == 0.0


def test_empty_input_does_not_divide_by_zero():
    report = classification_report([], [])

    assert report["accuracy"] == 0.0
    assert report["macro_f1"] == 0.0


def test_mismatched_lengths_raise():
    with pytest.raises(ValueError):
        confusion_matrix(["positive"], [])


def test_unknown_label_raises():
    with pytest.raises(ValueError):
        confusion_matrix(["happy"], ["positive"])
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `python -m pytest tests/test_metrics.py -q`
Expected: a collection error, `ModuleNotFoundError: No module named 'eval.metrics'`.

- [ ] **Step 3: Implement the metrics**

Create `backend/eval/metrics.py`:

```python
LABELS = ["positive", "neutral", "negative"]


def confusion_matrix(y_true: list[str], y_pred: list[str]) -> list[list[int]]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")

    index = {label: i for i, label in enumerate(LABELS)}
    matrix = [[0] * len(LABELS) for _ in LABELS]

    for true_label, predicted_label in zip(y_true, y_pred):
        if true_label not in index or predicted_label not in index:
            raise ValueError(f"unknown label: {true_label!r} or {predicted_label!r}")

        matrix[index[true_label]][index[predicted_label]] += 1

    return matrix


def _divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def classification_report(y_true: list[str], y_pred: list[str]) -> dict:
    matrix = confusion_matrix(y_true, y_pred)
    total = len(y_true)

    per_class = {}

    for i, label in enumerate(LABELS):
        true_positives = matrix[i][i]
        predicted = sum(row[i] for row in matrix)
        actual = sum(matrix[i])

        precision = _divide(true_positives, predicted)
        recall = _divide(true_positives, actual)
        f1 = _divide(2 * precision * recall, precision + recall)

        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": actual,
        }

    correct = sum(matrix[i][i] for i in range(len(LABELS)))

    return {
        "accuracy": _divide(correct, total),
        "macro_f1": sum(c["f1"] for c in per_class.values()) / len(LABELS),
        "per_class": per_class,
        "confusion_matrix": matrix,
    }
```

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests/test_metrics.py -q`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/eval/__init__.py backend/eval/metrics.py backend/tests/test_metrics.py
git commit -m "Add sentiment evaluation metrics" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 4: Scorer registry and evaluation harness

**Files:**
- Create: `backend/eval/scorers.py`
- Create: `backend/eval/evaluate.py`
- Create: `backend/requirements-eval.txt`
- Test: `backend/tests/test_evaluate.py`

**Interfaces:**
- Consumes: `LABELS`, `classification_report` (Task 3); `SentimentResult` (Task 1); `app.services.analysis.sentiment.score_comment` and `app.services.analysis.lexicon.score_comment` (Tasks 1 and 2).
- Produces: `Scorer = Callable[[str], SentimentResult]`; `SCORERS` (dict with `vader` and `lexicon`); `get_scorer(name) -> Scorer` (builds the transformer scorer lazily for `"transformer"`; raises `ValueError` for unknown names); `TRANSFORMER_MODEL`; in `eval.evaluate`: `load_dataset(path=DEFAULT_DATASET) -> list[dict]`, `evaluate(dataset, scorer_names, scorer_factory=get_scorer) -> dict[name, {"predictions": list[str], "report": dict}]`, `render_report(dataset, results, run_date) -> str`, `main(argv=None, scorer_factory=get_scorer)`, `DEFAULT_DATASET` (`backend/eval/data/labeled_comments.json`), `DEFAULT_OUTPUT` (`docs/sentiment-evaluation.md` at the repo root). Task 5 relies on `load_dataset`; Task 6 runs `main`.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_evaluate.py`:

```python
import json
import sys
from datetime import date

import pytest

from app.services.analysis.sentiment import SentimentResult
from eval.evaluate import evaluate, main, render_report
from eval.scorers import SCORERS, get_scorer

DATASET = [
    {"id": "a", "product_id": "p", "text": "good", "label": "positive", "source": "fixture"},
    {"id": "b", "product_id": "p", "text": "bad", "label": "negative", "source": "fixture"},
    {"id": "c", "product_id": "p", "text": "meh", "label": "neutral", "source": "fixture"},
]


def stub_factory(name):
    answers = {"good": "positive", "bad": "negative", "meh": "positive"}

    return lambda text: SentimentResult(label=answers[text], score=0.0)


def test_evaluate_runs_each_scorer_and_collects_predictions():
    results = evaluate(DATASET, ["stub"], scorer_factory=stub_factory)

    assert results["stub"]["predictions"] == ["positive", "negative", "positive"]
    assert results["stub"]["report"]["accuracy"] == pytest.approx(2 / 3)


def test_render_report_has_expected_sections_and_lists_mistakes():
    results = evaluate(DATASET, ["stub"], scorer_factory=stub_factory)

    report = render_report(DATASET, results, date(2026, 10, 1))

    assert "# Sentiment Evaluation" in report
    assert "Generated 2026-10-01" in report
    assert "3 hand-labeled comments (3 fixture)" in report
    assert "| stub | 0.667 |" in report
    assert "## stub" in report
    assert "### Misclassified" in report
    assert '"meh" — labeled **neutral**, predicted **positive**' in report
    assert "optimistic" in report


def test_main_writes_the_report_file(tmp_path):
    dataset_path = tmp_path / "data.json"
    dataset_path.write_text(json.dumps(DATASET), encoding="utf-8")
    output_path = tmp_path / "report.md"

    main(
        ["--scorers", "stub", "--dataset", str(dataset_path), "--output", str(output_path)],
        scorer_factory=stub_factory,
    )

    assert "## stub" in output_path.read_text(encoding="utf-8")


def test_registry_contains_the_lightweight_scorers():
    assert {"vader", "lexicon"} <= set(SCORERS)


def test_unknown_scorer_name_is_rejected():
    with pytest.raises(ValueError):
        get_scorer("nope")


def test_importing_the_registry_does_not_load_the_transformer_stack():
    assert "transformers" not in sys.modules
    assert "torch" not in sys.modules


def test_main_creates_a_missing_output_directory(tmp_path):
    dataset_path = tmp_path / "data.json"
    dataset_path.write_text(json.dumps(DATASET), encoding="utf-8")
    output_path = tmp_path / "docs" / "nested" / "report.md"

    main(
        ["--scorers", "stub", "--dataset", str(dataset_path), "--output", str(output_path)],
        scorer_factory=stub_factory,
    )

    assert output_path.exists()


def test_main_rejects_an_unknown_scorer_with_a_clean_error(tmp_path, capsys):
    dataset_path = tmp_path / "data.json"
    dataset_path.write_text(json.dumps(DATASET), encoding="utf-8")

    with pytest.raises(SystemExit) as exit_info:
        main(["--scorers", "nope", "--dataset", str(dataset_path), "--output", str(tmp_path / "r.md")])

    assert exit_info.value.code == 2
    assert "unknown scorer 'nope'" in capsys.readouterr().err
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `python -m pytest tests/test_evaluate.py -q`
Expected: a collection error, `ModuleNotFoundError: No module named 'eval.evaluate'`.

- [ ] **Step 3: Implement the registry**

Create `backend/eval/scorers.py`:

```python
from typing import Callable

from app.services.analysis import lexicon, sentiment
from app.services.analysis.sentiment import SentimentResult

Scorer = Callable[[str], SentimentResult]

TRANSFORMER_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

SCORERS: dict[str, Scorer] = {
    "vader": sentiment.score_comment,
    "lexicon": lexicon.score_comment,
}


def build_transformer_scorer() -> Scorer:
    from transformers import pipeline

    classifier = pipeline("sentiment-analysis", model=TRANSFORMER_MODEL)
    signs = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}

    def score_comment(text: str) -> SentimentResult:
        result = classifier(text, truncation=True)[0]
        label = result["label"].lower()

        return SentimentResult(label=label, score=signs[label] * result["score"])

    return score_comment


def get_scorer(name: str) -> Scorer:
    if name == "transformer":
        return build_transformer_scorer()

    if name not in SCORERS:
        raise ValueError(
            f"unknown scorer {name!r}; choose from {sorted([*SCORERS, 'transformer'])}"
        )

    return SCORERS[name]
```

- [ ] **Step 4: Implement the harness**

Create `backend/eval/evaluate.py`:

```python
import argparse
import json
from datetime import date
from pathlib import Path
from typing import Callable

from eval.metrics import LABELS, classification_report
from eval.scorers import TRANSFORMER_MODEL, Scorer, get_scorer

EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = EVAL_DIR / "data" / "labeled_comments.json"
DEFAULT_OUTPUT = EVAL_DIR.parents[1] / "docs" / "sentiment-evaluation.md"


def load_dataset(path: Path = DEFAULT_DATASET) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    dataset: list[dict],
    scorer_names: list[str],
    scorer_factory: Callable[[str], Scorer] = get_scorer,
) -> dict[str, dict]:
    y_true = [item["label"] for item in dataset]
    results = {}

    for name in scorer_names:
        scorer = scorer_factory(name)
        y_pred = [scorer(item["text"]).label for item in dataset]

        results[name] = {
            "predictions": y_pred,
            "report": classification_report(y_true, y_pred),
        }

    return results


def _confusion_table(matrix: list[list[int]]) -> str:
    header = "| true \\ predicted | " + " | ".join(LABELS) + " |"
    divider = "|---|" + "---|" * len(LABELS)
    rows = [
        f"| **{label}** | " + " | ".join(str(n) for n in row) + " |"
        for label, row in zip(LABELS, matrix)
    ]

    return "\n".join([header, divider, *rows])


def render_report(
    dataset: list[dict],
    results: dict[str, dict],
    run_date: date,
) -> str:
    sources: dict[str, int] = {}

    for item in dataset:
        sources[item["source"]] = sources.get(item["source"], 0) + 1

    source_text = ", ".join(f"{count} {name}" for name, count in sorted(sources.items()))

    lines = [
        "# Sentiment Evaluation",
        "",
        f"Generated {run_date.isoformat()} by `python -m eval.evaluate`.",
        "",
        "## Dataset",
        "",
        f"{len(dataset)} hand-labeled comments ({source_text}).",
        "",
        "> **Read this before the numbers.** The `fixture` comments were written for"
        " this project, so they are cleaner than real Reddit text and these scores are"
        " optimistic. The lexicon was authored by someone who had already seen the"
        " fixtures, which is a small contamination risk. Thresholds are VADER's"
        " defaults (+/-0.05) and were not tuned on this data. The evaluation will be"
        " re-run on real Reddit comments after ingestion.",
        "",
        "## Summary",
        "",
        "| scorer | accuracy | macro-F1 |",
        "|---|---|---|",
    ]

    for name, result in results.items():
        report = result["report"]
        lines.append(f"| {name} | {report['accuracy']:.3f} | {report['macro_f1']:.3f} |")

    if "transformer" in results:
        lines += ["", f"Transformer model: `{TRANSFORMER_MODEL}` (run locally, not in CI)."]

    for name, result in results.items():
        report = result["report"]

        lines += [
            "",
            f"## {name}",
            "",
            "| class | precision | recall | F1 | support |",
            "|---|---|---|---|---|",
        ]

        for label in LABELS:
            c = report["per_class"][label]
            lines.append(
                f"| {label} | {c['precision']:.3f} | {c['recall']:.3f}"
                f" | {c['f1']:.3f} | {c['support']} |"
            )

        lines += ["", _confusion_table(report["confusion_matrix"]), "", "### Misclassified", ""]

        wrong = [
            (item, predicted)
            for item, predicted in zip(dataset, result["predictions"])
            if item["label"] != predicted
        ]

        if not wrong:
            lines.append("None.")

        for item, predicted in wrong:
            lines.append(
                f"- \"{item['text']}\" — labeled **{item['label']}**, predicted **{predicted}**"
            )

    return "\n".join(lines) + "\n"


def main(
    argv: list[str] | None = None,
    scorer_factory: Callable[[str], Scorer] = get_scorer,
) -> None:
    parser = argparse.ArgumentParser(description="Evaluate sentiment scorers.")
    parser.add_argument("--scorers", default="vader,lexicon")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    dataset = load_dataset(args.dataset)

    try:
        results = evaluate(dataset, args.scorers.split(","), scorer_factory)
    except ValueError as error:
        parser.error(str(error))

    for name, result in results.items():
        report = result["report"]
        print(f"{name}: accuracy={report['accuracy']:.3f} macro_f1={report['macro_f1']:.3f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_report(dataset, results, date.today()), encoding="utf-8"
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Add the eval-only requirements**

Create `backend/requirements-eval.txt`:

```text
transformers==5.18.0
torch==2.14.1
```

Do not install it here; Task 6 uses it in a separate environment.

- [ ] **Step 6: Run the tests**

Run: `python -m pytest tests/test_evaluate.py -q`
Expected: 8 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/eval/scorers.py backend/eval/evaluate.py backend/requirements-eval.txt backend/tests/test_evaluate.py
git commit -m "Add scorer registry and evaluation harness" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 5: Labeled dataset

**Files:**
- Create: `backend/eval/data/labeled_comments.json` (generated by a throwaway script, then reviewed)
- Test: `backend/tests/test_labeled_dataset.py`

**Interfaces:**
- Consumes: `load_dataset` from `eval.evaluate` (Task 4); `LABELS` (Task 3); `app.data.comments.comments` (dict of product id to list of comment strings, in a fixed order).
- Produces: `backend/eval/data/labeled_comments.json`: a list of `{"id": "fixture-NNN", "product_id": str, "text": str, "label": "positive"|"neutral"|"negative", "source": "fixture"}`, 50 items in `comments.py` order. These are **draft labels** until the review gate in Task 6.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_labeled_dataset.py`:

```python
from collections import Counter

from app.data.comments import comments
from eval.evaluate import load_dataset
from eval.metrics import LABELS

SOURCES = {"fixture", "reddit"}


def test_every_item_is_well_formed():
    for item in load_dataset():
        assert set(item) == {"id", "product_id", "text", "label", "source"}
        assert item["label"] in LABELS
        assert item["source"] in SOURCES
        assert item["text"].strip()


def test_ids_are_unique():
    ids = [item["id"] for item in load_dataset()]

    assert len(ids) == len(set(ids))


def test_every_fixture_comment_appears_exactly_once_with_its_product():
    fixture_items = [i for i in load_dataset() if i["source"] == "fixture"]
    labeled = Counter((i["product_id"], i["text"]) for i in fixture_items)
    expected = Counter(
        (product_id, text)
        for product_id, texts in comments.items()
        for text in texts
    )

    assert labeled == expected
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `python -m pytest tests/test_labeled_dataset.py -q`
Expected: 3 failed with `FileNotFoundError` for `eval/data/labeled_comments.json`.

- [ ] **Step 3: Generate the draft dataset**

Create the directory `backend/eval/data/`, then write this throwaway script to a scratch path outside the repo (for example `$TMPDIR/make_dataset.py`) and run it from `backend/` with `PYTHONPATH=.`. Do not commit the script. Labels were drafted as follows: a comment praising one thing and criticizing another with no clear net lean is `neutral`.

```python
import json

from app.data.comments import comments

LABELS = {
    "airpods-pro": "positive negative positive neutral negative positive positive neutral positive negative positive neutral negative neutral negative positive negative positive",
    "sony-wh-1000xm6": "positive positive positive negative negative neutral positive negative positive negative neutral negative positive neutral negative positive",
    "steam-deck-oled": "positive positive negative positive negative negative positive positive negative positive neutral negative positive negative neutral positive",
}

items = []

for product_id, texts in comments.items():
    labels = LABELS[product_id].split()
    assert len(labels) == len(texts), (product_id, len(labels), len(texts))

    for text, label in zip(texts, labels):
        items.append(
            {
                "id": f"fixture-{len(items) + 1:03d}",
                "product_id": product_id,
                "text": text,
                "label": label,
                "source": "fixture",
            }
        )

with open("eval/data/labeled_comments.json", "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(len(items), "items written")
```

Run: `PYTHONPATH=. python "$TMPDIR/make_dataset.py"`
Expected: `50 items written`.

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests/test_labeled_dataset.py -q`
Expected: 3 passed.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest -q`
Expected: 83 passed (34 existing plus 49 new).

- [ ] **Step 6: Commit the draft labels**

```bash
git add backend/eval/data/labeled_comments.json backend/tests/test_labeled_dataset.py
git commit -m "Add draft labeled sentiment dataset" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 6: Review gate, evaluation run and report

**Files:**
- Modify: `backend/eval/data/labeled_comments.json` (only if the user corrects labels)
- Create (generated): `docs/sentiment-evaluation.md`

**Interfaces:**
- Consumes: everything above. `python -m eval.evaluate --scorers vader,lexicon[,transformer]` writes `docs/sentiment-evaluation.md`.
- Produces: the committed report.

- [ ] **Step 1: REVIEW GATE: stop and ask the user to review the labels**

This is a required stop, authorized by the spec: **no evaluation numbers may be generated or reported before the author has reviewed the labels.** Do not run the harness yet. Print a numbered review table with:

```bash
python - <<'PY'
import json
for i, item in enumerate(json.load(open("eval/data/labeled_comments.json", encoding="utf-8")), 1):
    print(f"{i:2} {item['label']:<9} {item['text']}")
PY
```

Then show the user the table and ask them to reply with either "labels approved" or a list of corrections (for example "7 -> negative"). Explain the rule used for `neutral` (mixed praise and criticism with no clear net lean). Wait for their reply.

- [ ] **Step 2: Apply corrections, if any**

For each correction, edit the matching item's `"label"` in `backend/eval/data/labeled_comments.json` with the Edit tool (the file has one label per item; find it by its text). Then run `python -m pytest tests/test_labeled_dataset.py -q`.
Expected: 3 passed. Commit with `git add backend/eval/data/labeled_comments.json` and the message "Apply reviewed sentiment labels". Skip the commit if no corrections were made.

- [ ] **Step 3: Run the lightweight evaluation**

Run: `python -m eval.evaluate --scorers vader,lexicon`
Expected: two lines `vader: accuracy=... macro_f1=...` and `lexicon: accuracy=... macro_f1=...`, then `wrote .../docs/sentiment-evaluation.md`. Read the generated report. Check that the dataset size is 50, that each confusion matrix sums to 50, and that the misclassified lists are plausible.

- [ ] **Step 4: Transformer run (ask first)**

The transformer needs about 2 to 3 GB of downloads (PyTorch plus the model weights). Ask the user whether to run it now. If they say yes:

```bash
python3.13 -m venv "$HOME/.cache/psa-eval-venv"
"$HOME/.cache/psa-eval-venv/bin/pip" install -r requirements.txt -r requirements-eval.txt
"$HOME/.cache/psa-eval-venv/bin/python" -m eval.evaluate --scorers vader,lexicon,transformer
```

Expected: three metric lines and a regenerated report that includes a `transformer` section and the model name. The venv lives outside the repository on purpose.
If the user declines, keep the two-scorer report and state in the final message that the transformer comparison, which the spec calls for, is still pending.

- [ ] **Step 5: Add a short interpretation to the report**

Below the generated "Summary" table in `docs/sentiment-evaluation.md`, add a section titled `## Findings` with 3 to 5 sentences written from the real results: which scorer was best on macro-F1, how every scorer did on the `neutral` class, and one concrete pattern from the misclassified examples. Do not claim anything the numbers do not show. Note that re-running `python -m eval.evaluate` regenerates the file and discards this section, so keep a copy before re-running.

- [ ] **Step 6: Commit the report**

```bash
git add docs/sentiment-evaluation.md
git commit -m "Add sentiment evaluation report" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
```

---

### Task 7: Docs

**Files:**
- Modify: `CLAUDE.md`, `README.md`, `docs/plan.md`

**Interfaces:**
- Consumes: the finished feature.
- Produces: updated commands and links.

`CLAUDE.md` and `README.md` contain the user's uncommitted edits. Stage only these changes by writing HEAD-based blobs into the index, then apply the same edits to the working files.

- [ ] **Step 1: Apply and stage the edits**

Run from the repository root (not `backend/`):

```bash
python3 - <<'PY'
import subprocess


def head(path):
    return subprocess.run(
        ["git", "show", "HEAD:" + path], capture_output=True, text=True, check=True
    ).stdout


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def claude(text):
    text = replace_once(
        text,
        "pytest tests/test_textanalysis.py::test_clean_text   # single test\n",
        "pytest tests/test_textanalysis.py::test_clean_text   # single test\n"
        "python -m eval.evaluate --scorers vader,lexicon       # regenerates docs/sentiment-evaluation.md; add `transformer` only in an env with requirements-eval.txt\n",
    )
    return replace_once(
        text,
        "which nothing consumes yet.\n",
        "which nothing consumes yet.\n"
        "- **Sentiment (`services/analysis/sentiment.py`, `lexicon.py`) and evaluation (`backend/eval/`):** both scorers share one signature, `score_comment(text) -> SentimentResult(label, score)`. `eval/` is outside the app: a scorer registry, hand-written metrics, and a CLI that scores `eval/data/labeled_comments.json` and writes `docs/sentiment-evaluation.md`. The transformer scorer is imported lazily and its dependencies live only in `requirements-eval.txt`, so CI and the deployed API never install them. The API does not use sentiment yet (that is 0.3 part 2).\n",
    )


def readme(text):
    return replace_once(
        text,
        "- Unit tests with pytest\n",
        "- Unit tests with pytest\n"
        "- Sentiment scoring (VADER and a hand-built lexicon) with an [evaluation report](docs/sentiment-evaluation.md)\n",
    )


def plan(text):
    for item in [
        "`services/analysis/sentiment.py` with `score_comment(text)`",
        "Use VADER (`vaderSentiment`)",
        "Optional: a hand-built lexicon scorer",
    ]:
        text = replace_once(text, "- [ ] " + item, "- [x] " + item)

    return replace_once(
        text,
        "- [ ] Hand-labeled evaluation set (`backend/tests/fixtures/labeled_comments.json`) and an accuracy report",
        "- [x] Hand-labeled evaluation set (`backend/eval/data/labeled_comments.json`) and an evaluation report (`docs/sentiment-evaluation.md`)",
    )


for path, edit in [("CLAUDE.md", claude), ("README.md", readme), ("docs/plan.md", plan)]:
    new_head = edit(head(path))
    blob = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        input=new_head, capture_output=True, text=True, check=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "update-index", "--cacheinfo", f"100644,{blob},{path}"], check=True
    )

    with open(path, encoding="utf-8") as f:
        current = f.read()

    updated = edit(current)

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
PY
wc -c CLAUDE.md README.md docs/plan.md
git diff --cached --stat
git diff --stat
```

Expected: no assertion errors; none of the three byte counts is 0; `git diff --cached --stat` lists only `CLAUDE.md`, `README.md` and `docs/plan.md` with small insertions (about 2, 1 and 4 lines changed); `git diff --stat` still shows the user's own Docker hunks in `CLAUDE.md` and `README.md`. If a count is 0 or an assertion fails, stop and recover from `git show HEAD:<file>`.

- [ ] **Step 2: Final verification**

Run: `cd backend && python -m pytest -q`
Expected: 83 passed.

- [ ] **Step 3: Commit**

```bash
git commit -m "Document sentiment scoring and evaluation" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R89pfHE1NRDsvAHzyz4348"
git status --short
```
Expected: only the user's unrelated files remain uncommitted.

---

## Self-Review Notes

- **Spec coverage:** `sentiment.py` and `aggregate_sentiment` (Task 1), `lexicon.py` (Task 2), `metrics.py` (Task 3), `scorers.py`, `evaluate.py`, `requirements-eval.txt` (Task 4), the labeled dataset and its validation tests (Task 5), the label review gate, report, transformer run and honesty text (Tasks 4 and 6), CI-safe tests with no transformer (all tasks), docs (Task 7).
- **Spec points carried verbatim:** thresholds, three labels, VADER pinned, transformer lazy and eval-only, the optimistic-scores and lexicon-contamination notes in the report template inside `render_report`.
- **Names used across tasks:** `SentimentResult`, `label_for_score`, `score_comment`, `LABELS`, `classification_report`, `get_scorer`, `load_dataset`, `evaluate`, `render_report`, `main` all match their definitions.
- **Provenance:** every code block and test was run in a scratch copy of the backend before being written here (83 tests passing there).
