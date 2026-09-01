import re

from app.services.analysis.stopwords import STOP_WORDS


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text: str) -> list[str]:
    cleaned_text = clean_text(text)
    return cleaned_text.split()


def remove_stop_words(tokens: list[str]) -> list[str]:
    filtered_tokens = []

    for token in tokens:
        if token not in STOP_WORDS:
            filtered_tokens.append(token)

    return filtered_tokens