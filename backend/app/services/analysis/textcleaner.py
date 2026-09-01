import re


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def tokenize(text: str) -> list[str]:
    cleaned_text = clean_text(text)

    return cleaned_text.split()