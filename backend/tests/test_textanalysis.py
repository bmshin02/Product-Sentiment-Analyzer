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