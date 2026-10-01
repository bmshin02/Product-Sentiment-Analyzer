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
