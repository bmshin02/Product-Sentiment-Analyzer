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
