import re

from app.services.analysis.stopwords import STOP_WORDS


IRREGULAR_CONTRACTIONS = {
    "can't": "can not",
    "won't": "will not",
    "shan't": "shall not",
}

CONTRACTION_SUFFIXES = {
    "n't": " not",
    "'re": " are",
    "'ve": " have",
    "'ll": " will",
    "'m": " am",
    "'d": " would",
}


def expand_contractions(text: str) -> str:
    text = text.replace("\u2019", "'")

    for contraction, expansion in IRREGULAR_CONTRACTIONS.items():
        text = re.sub(rf"\b{contraction}\b", expansion, text)

    for suffix, expansion in CONTRACTION_SUFFIXES.items():
        text = re.sub(rf"(?<=\w){re.escape(suffix)}\b", expansion, text)

    return text


def clean_text(text: str) -> str:
    text = text.lower()
    text = expand_contractions(text)
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