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

    frequencies = {}

    for token in all_tokens:
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1

    return frequencies

def get_top_words(
    texts: list[str],
    limit: int = 10,
) -> list[tuple[str, int]]:
    frequencies = get_word_frequencies(texts)

    sorted_words = sorted(
        frequencies.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return sorted_words[:limit]