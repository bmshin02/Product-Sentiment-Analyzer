import json
import sys
from datetime import date

import pytest

from app.services.analysis.sentiment import SentimentResult
from eval.evaluate import evaluate, main, render_report
from eval.scorers import SCORERS, get_scorer

DATASET = [
    {"id": "a", "product_id": "p", "text": "good", "label": "positive", "source": "fixture"},
    {"id": "b", "product_id": "p", "text": "bad", "label": "negative", "source": "fixture"},
    {"id": "c", "product_id": "p", "text": "meh", "label": "neutral", "source": "fixture"},
]


def stub_factory(name):
    answers = {"good": "positive", "bad": "negative", "meh": "positive"}

    return lambda text: SentimentResult(label=answers[text], score=0.0)


def test_evaluate_runs_each_scorer_and_collects_predictions():
    results = evaluate(DATASET, ["stub"], scorer_factory=stub_factory)

    assert results["stub"]["predictions"] == ["positive", "negative", "positive"]
    assert results["stub"]["report"]["accuracy"] == pytest.approx(2 / 3)


def test_render_report_has_expected_sections_and_lists_mistakes():
    results = evaluate(DATASET, ["stub"], scorer_factory=stub_factory)

    report = render_report(DATASET, results, date(2026, 10, 1))

    assert "# Sentiment Evaluation" in report
    assert "Generated 2026-10-01" in report
    assert "3 hand-labeled comments (3 fixture)" in report
    assert "| stub | 0.667 |" in report
    assert "## stub" in report
    assert "### Misclassified" in report
    assert '"meh" — labeled **neutral**, predicted **positive**' in report
    assert "optimistic" in report


def test_main_writes_the_report_file(tmp_path):
    dataset_path = tmp_path / "data.json"
    dataset_path.write_text(json.dumps(DATASET), encoding="utf-8")
    output_path = tmp_path / "report.md"

    main(
        ["--scorers", "stub", "--dataset", str(dataset_path), "--output", str(output_path)],
        scorer_factory=stub_factory,
    )

    assert "## stub" in output_path.read_text(encoding="utf-8")


def test_registry_contains_the_lightweight_scorers():
    assert {"vader", "lexicon"} <= set(SCORERS)


def test_unknown_scorer_name_is_rejected():
    with pytest.raises(ValueError):
        get_scorer("nope")


def test_importing_the_registry_does_not_load_the_transformer_stack():
    assert "transformers" not in sys.modules
    assert "torch" not in sys.modules


def test_main_creates_a_missing_output_directory(tmp_path):
    dataset_path = tmp_path / "data.json"
    dataset_path.write_text(json.dumps(DATASET), encoding="utf-8")
    output_path = tmp_path / "docs" / "nested" / "report.md"

    main(
        ["--scorers", "stub", "--dataset", str(dataset_path), "--output", str(output_path)],
        scorer_factory=stub_factory,
    )

    assert output_path.exists()


def test_main_rejects_an_unknown_scorer_with_a_clean_error(tmp_path, capsys):
    dataset_path = tmp_path / "data.json"
    dataset_path.write_text(json.dumps(DATASET), encoding="utf-8")

    with pytest.raises(SystemExit) as exit_info:
        main(["--scorers", "nope", "--dataset", str(dataset_path), "--output", str(tmp_path / "r.md")])

    assert exit_info.value.code == 2
    assert "unknown scorer 'nope'" in capsys.readouterr().err
