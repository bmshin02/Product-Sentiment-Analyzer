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

def get_ngrams(tokens: list[str], n: int) -> list[tuple]:
    ngrams = []

    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i:i + n])
        ngrams.append(ngram)

    return ngrams

def get_ngram_frequencies(
    texts: list[str],
    n: int,
) -> dict[tuple, int]:
    frequencies = {}

    for text in texts:
        tokens = tokenize(text)
        tokens = remove_stop_words(tokens)

        ngrams = get_ngrams(tokens, n)

        for ngram in ngrams:
            if ngram in frequencies:
                frequencies[ngram] += 1
            else:
                frequencies[ngram] = 1

    return frequencies

def get_top_ngrams(
    texts: list[str],
    n: int,
    limit: int = 10,
) -> list[tuple[tuple, int]]:
    frequencies = get_ngram_frequencies(texts, n)

    sorted_ngrams = sorted(
        frequencies.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return sorted_ngrams[:limit]