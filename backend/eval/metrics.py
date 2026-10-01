LABELS = ["positive", "neutral", "negative"]


def confusion_matrix(y_true: list[str], y_pred: list[str]) -> list[list[int]]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")

    index = {label: i for i, label in enumerate(LABELS)}
    matrix = [[0] * len(LABELS) for _ in LABELS]

    for true_label, predicted_label in zip(y_true, y_pred):
        if true_label not in index or predicted_label not in index:
            raise ValueError(f"unknown label: {true_label!r} or {predicted_label!r}")

        matrix[index[true_label]][index[predicted_label]] += 1

    return matrix


def _divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def classification_report(y_true: list[str], y_pred: list[str]) -> dict:
    matrix = confusion_matrix(y_true, y_pred)
    total = len(y_true)

    per_class = {}

    for i, label in enumerate(LABELS):
        true_positives = matrix[i][i]
        predicted = sum(row[i] for row in matrix)
        actual = sum(matrix[i])

        precision = _divide(true_positives, predicted)
        recall = _divide(true_positives, actual)
        f1 = _divide(2 * precision * recall, precision + recall)

        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": actual,
        }

    correct = sum(matrix[i][i] for i in range(len(LABELS)))

    return {
        "accuracy": _divide(correct, total),
        "macro_f1": sum(c["f1"] for c in per_class.values()) / len(LABELS),
        "per_class": per_class,
        "confusion_matrix": matrix,
    }
