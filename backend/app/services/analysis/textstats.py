from collections import Counter

from app.services.analysis.textcleaner import tokenize


def get_word_frequencies(texts: list[str]) -> dict[str, int]:
    all_tokens = []

    for text in texts:
        all_tokens.extend(tokenize(text))

    return dict(Counter(all_tokens))