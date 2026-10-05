from app.schemas.product import WordCount
from app.services.analysis.wordsentiment import get_sentiment_words


def test_words_are_bucketed_by_polarity():
    positives, negatives = get_sentiment_words(["great battery but terrible price"])

    assert positives == [WordCount(word="great", count=1)]
    assert negatives == [WordCount(word="terrible", count=1)]


def test_negated_positive_word_moves_to_negatives():
    positives, negatives = get_sentiment_words(["good, not amazing for the price"])

    assert positives == [WordCount(word="good", count=1)]
    assert negatives == [WordCount(word="amazing", count=1)]


def test_negated_negative_word_moves_to_positives():
    positives, negatives = get_sentiment_words(["it is not bad"])

    assert positives == [WordCount(word="bad", count=1)]
    assert negatives == []


def test_plain_and_negated_uses_land_in_their_own_lists():
    positives, negatives = get_sentiment_words(["really good", "not good"])

    assert positives == [WordCount(word="good", count=1)]
    assert negatives == [WordCount(word="good", count=1)]


def test_negation_scope_breaker_keeps_word_plain():
    positives, negatives = get_sentiment_words(["not cheap but great"])

    assert positives == [WordCount(word="great", count=1)]


def test_counts_accumulate_across_comments():
    positives, _ = get_sentiment_words(["great sound", "great fit", "nice case"])

    assert positives[0] == WordCount(word="great", count=2)


def test_ties_are_sorted_alphabetically():
    positives, _ = get_sentiment_words(["nice", "great", "good"])

    assert [item.word for item in positives] == ["good", "great", "nice"]


def test_limit_caps_each_list():
    positives, _ = get_sentiment_words(["great nice good fine"], limit=2)

    assert len(positives) == 2


def test_neutral_and_unknown_words_are_ignored():
    assert get_sentiment_words(["the battery case"]) == ([], [])


def test_empty_input_returns_empty_lists():
    assert get_sentiment_words([]) == ([], [])
    assert get_sentiment_words([""]) == ([], [])


def test_comparatives_are_left_out_of_the_lists():
    texts = ["I expected better", "works better than before", "it got worse"]

    assert get_sentiment_words(texts) == ([], [])
