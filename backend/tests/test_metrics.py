import pytest

from eval.metrics import LABELS, classification_report, confusion_matrix

Y_TRUE = ["positive", "positive", "negative", "neutral"]
Y_PRED = ["positive", "negative", "negative", "positive"]


def test_labels_order():
    assert LABELS == ["positive", "neutral", "negative"]


def test_confusion_matrix_rows_are_true_labels_columns_are_predictions():
    assert confusion_matrix(Y_TRUE, Y_PRED) == [
        [1, 0, 1],
        [1, 0, 0],
        [0, 0, 1],
    ]


def test_classification_report_matches_hand_computed_values():
    report = classification_report(Y_TRUE, Y_PRED)

    assert report["accuracy"] == pytest.approx(0.5)
    assert report["per_class"]["positive"] == pytest.approx(
        {"precision": 0.5, "recall": 0.5, "f1": 0.5, "support": 2}
    )
    assert report["per_class"]["negative"] == pytest.approx(
        {"precision": 0.5, "recall": 1.0, "f1": 2 / 3, "support": 1}
    )
    assert report["macro_f1"] == pytest.approx((0.5 + 0.0 + 2 / 3) / 3)


def test_class_with_no_predictions_scores_zero_not_an_error():
    report = classification_report(Y_TRUE, Y_PRED)

    assert report["per_class"]["neutral"] == {
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "support": 1,
    }


def test_class_with_no_examples_scores_zero_not_an_error():
    report = classification_report(["positive", "positive"], ["positive", "positive"])

    assert report["accuracy"] == 1.0
    assert report["per_class"]["negative"]["support"] == 0
    assert report["per_class"]["negative"]["f1"] == 0.0


def test_empty_input_does_not_divide_by_zero():
    report = classification_report([], [])

    assert report["accuracy"] == 0.0
    assert report["macro_f1"] == 0.0


def test_mismatched_lengths_raise():
    with pytest.raises(ValueError):
        confusion_matrix(["positive"], [])


def test_unknown_label_raises():
    with pytest.raises(ValueError):
        confusion_matrix(["happy"], ["positive"])
