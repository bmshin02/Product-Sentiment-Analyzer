import math

from app.services.analysis.sentiment import SentimentResult, label_for_score
from app.services.analysis.textcleaner import tokenize

LEXICON = {
    # strongly positive
    "amazing": 3, "amazingly": 3, "awesome": 3, "best": 3, "excellent": 3,
    "fantastic": 3, "flawless": 3, "flawlessly": 3, "gorgeous": 3,
    "incredible": 3, "love": 3, "loved": 3, "outstanding": 3, "perfect": 3,
    "stunning": 3,
    # positive
    "beautiful": 2, "bright": 2, "clear": 2, "comfortable": 2,
    "comfortably": 2, "convenient": 2, "crisp": 2, "enjoy": 2, "fast": 2,
    "good": 2, "great": 2, "happy": 2, "impressive": 2, "natural": 2,
    "nice": 2, "quiet": 2, "quieter": 2, "recommend": 2, "reliable": 2,
    "seamless": 2, "smooth": 2, "solid": 2, "sturdy": 2, "worth": 2,
    # mildly positive
    "better": 1, "decent": 1, "easy": 1, "fine": 1, "improved": 1,
    "pleasant": 1, "useful": 1,
    # strongly negative
    "awful": -3, "broken": -3, "disappointing": -3, "garbage": -3,
    "hate": -3, "hated": -3, "horrible": -3, "ridiculous": -3,
    "ridiculously": -3, "terrible": -3, "unusable": -3, "useless": -3,
    "worst": -3,
    # negative
    "annoying": -2, "bad": -2, "buggy": -2, "disappointed": -2, "dying": -2,
    "expensive": -2, "fails": -2, "flimsy": -2, "laggy": -2, "mediocre": -2,
    "noisy": -2, "overpriced": -2, "poor": -2, "slow": -2, "struggle": -2,
    "struggles": -2, "uncomfortable": -2, "worse": -2,
    # mildly negative
    "bulky": -1, "heavy": -1, "issue": -1, "issues": -1, "lack": -1,
    "limited": -1, "pricey": -1, "problem": -1, "tight": -1, "wish": -1,
}

NEGATORS = {"not", "no", "never", "cannot", "hardly"}
INTENSIFIERS = {
    "very", "really", "super", "extremely", "incredibly", "absolutely",
    "so", "too", "way",
}
SCOPE_BREAKERS = {"but", "however", "although"}

NEGATION_WINDOW = 3
NEGATION_FACTOR = -0.5
INTENSIFIER_FACTOR = 1.5
NORMALIZATION_ALPHA = 15


def _is_negated(tokens: list[str], index: int) -> bool:
    for previous in reversed(tokens[max(0, index - NEGATION_WINDOW):index]):
        if previous in SCOPE_BREAKERS:
            return False

        if previous in NEGATORS:
            return True

    return False


def _is_intensified(tokens: list[str], index: int) -> bool:
    return any(token in INTENSIFIERS for token in tokens[max(0, index - 2):index])


def score_comment(text: str) -> SentimentResult:
    tokens = tokenize(text)
    total = 0.0

    for index, token in enumerate(tokens):
        polarity = LEXICON.get(token)

        if polarity is None:
            continue

        value = float(polarity)

        if _is_intensified(tokens, index):
            value *= INTENSIFIER_FACTOR

        if _is_negated(tokens, index):
            value *= NEGATION_FACTOR

        total += value

    score = total / math.sqrt(total * total + NORMALIZATION_ALPHA)

    return SentimentResult(label=label_for_score(score), score=score)
