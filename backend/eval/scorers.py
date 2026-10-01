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
