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
