from app.services.analysis.textcleaner import (
    clean_text,
    remove_stop_words,
    tokenize,
)
from app.services.analysis.textstats import get_ngrams

def test_clean_text():
    result = clean_text("The Battery is REALLY good!!!")

    assert result == "the battery is really good"

def test_tokenize():
    result = tokenize("Battery life is great!")

    assert result == [
        "battery",
        "life",
        "is",
        "great",
    ]

def test_remove_stop_words():
    tokens = [
        "the",
        "battery",
        "is",
        "really",
        "good",
    ]

    result = remove_stop_words(tokens)

    assert result == [
        "battery",
        "really",
        "good",
    ]

def test_stop_words_preserve_not():
    tokens = [
        "the",
        "battery",
        "is",
        "not",
        "good",
    ]

    result = remove_stop_words(tokens)

    assert "not" in result

def test_get_bigrams():
    tokens = [
        "battery",
        "life",
        "great",
    ]

    result = get_ngrams(tokens, 2)

    assert result == [
        ("battery", "life"),
        ("life", "great"),
    ]

def test_get_trigrams():
    tokens = [
        "active",
        "noise",
        "cancellation",
        "great",
    ]

    result = get_ngrams(tokens, 3)

    assert result == [
        ("active", "noise", "cancellation"),
        ("noise", "cancellation", "great"),
    ]


def test_clean_text_expands_negative_contractions():
    assert clean_text("It isn't good") == "it is not good"
    assert clean_text("I don't like it") == "i do not like it"
    assert clean_text("They can't connect") == "they can not connect"
    assert clean_text("It won't pair") == "it will not pair"


def test_clean_text_expands_other_contractions():
    assert clean_text("They're great") == "they are great"
    assert clean_text("I've had them a year") == "i have had them a year"
    assert clean_text("I'm happy") == "i am happy"


def test_clean_text_handles_curly_apostrophes():
    assert clean_text("It isn\u2019t good") == "it is not good"


def test_negation_survives_tokenize_and_stop_words():
    tokens = remove_stop_words(tokenize("The battery isn't terrible"))

    assert "not" in tokens
