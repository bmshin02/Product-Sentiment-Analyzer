from collections import Counter

from app.services.analysis.textcleaner import (
    remove_stop_words,
    tokenize,
)


def get_word_frequencies(texts: list[str]) -> dict[str, int]:
    all_tokens = []

    for text in texts:
        all_tokens.extend(tokenize(text))

    all_tokens = remove_stop_words(all_tokens)

    return dict(Counter(all_tokens))