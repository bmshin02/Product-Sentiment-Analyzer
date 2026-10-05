from app.schemas.product import WordCount
from app.services.analysis.lexicon import LEXICON, is_negated
from app.services.analysis.textcleaner import tokenize

# Comparatives are used for both praise and complaints ("expected better"),
# so a single word can't be bucketed reliably.
COMPARATIVES = {"better", "worse"}


def _top_words(counts: dict[str, int], limit: int) -> list[WordCount]:
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    return [WordCount(word=word, count=count) for word, count in ranked[:limit]]


def get_sentiment_words(
    texts: list[str],
    limit: int = 5,
) -> tuple[list[WordCount], list[WordCount]]:
    positive_counts: dict[str, int] = {}
    negative_counts: dict[str, int] = {}

    for text in texts:
        tokens = tokenize(text)

        for index, token in enumerate(tokens):
            polarity = LEXICON.get(token)

            if polarity is None or token in COMPARATIVES:
                continue

            if is_negated(tokens, index):
                polarity = -polarity

            counts = positive_counts if polarity > 0 else negative_counts
            counts[token] = counts.get(token, 0) + 1

    return _top_words(positive_counts, limit), _top_words(negative_counts, limit)
