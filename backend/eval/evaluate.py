import argparse
import json
from datetime import date
from pathlib import Path
from typing import Callable

from eval.metrics import LABELS, classification_report
from eval.scorers import TRANSFORMER_MODEL, Scorer, get_scorer

EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = EVAL_DIR / "data" / "labeled_comments.json"
DEFAULT_OUTPUT = EVAL_DIR.parents[1] / "docs" / "sentiment-evaluation.md"


def load_dataset(path: Path = DEFAULT_DATASET) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    dataset: list[dict],
    scorer_names: list[str],
    scorer_factory: Callable[[str], Scorer] = get_scorer,
) -> dict[str, dict]:
    y_true = [item["label"] for item in dataset]
    results = {}

    for name in scorer_names:
        scorer = scorer_factory(name)
        y_pred = [scorer(item["text"]).label for item in dataset]

        results[name] = {
            "predictions": y_pred,
            "report": classification_report(y_true, y_pred),
        }

    return results


def _confusion_table(matrix: list[list[int]]) -> str:
    header = "| true \\ predicted | " + " | ".join(LABELS) + " |"
    divider = "|---|" + "---|" * len(LABELS)
    rows = [
        f"| **{label}** | " + " | ".join(str(n) for n in row) + " |"
        for label, row in zip(LABELS, matrix)
    ]

    return "\n".join([header, divider, *rows])


def render_report(
    dataset: list[dict],
    results: dict[str, dict],
    run_date: date,
) -> str:
    sources: dict[str, int] = {}

    for item in dataset:
        sources[item["source"]] = sources.get(item["source"], 0) + 1

    source_text = ", ".join(f"{count} {name}" for name, count in sorted(sources.items()))

    lines = [
        "# Sentiment Evaluation",
        "",
        f"Generated {run_date.isoformat()} by `python -m eval.evaluate`.",
        "",
        "## Dataset",
        "",
        f"{len(dataset)} hand-labeled comments ({source_text}).",
        "",
        "> **Read this before the numbers.** The `fixture` comments were written for"
        " this project, so they are cleaner than real Reddit text and these scores are"
        " optimistic. The lexicon was authored by someone who had already seen the"
        " fixtures, which is a small contamination risk. Thresholds are VADER's"
        " defaults (+/-0.05) and were not tuned on this data. The evaluation will be"
        " re-run on real Reddit comments after ingestion.",
        "",
        "## Summary",
        "",
        "| scorer | accuracy | macro-F1 |",
        "|---|---|---|",
    ]

    for name, result in results.items():
        report = result["report"]
        lines.append(f"| {name} | {report['accuracy']:.3f} | {report['macro_f1']:.3f} |")

    if "transformer" in results:
        lines += ["", f"Transformer model: `{TRANSFORMER_MODEL}` (run locally, not in CI)."]

    for name, result in results.items():
        report = result["report"]

        lines += [
            "",
            f"## {name}",
            "",
            "| class | precision | recall | F1 | support |",
            "|---|---|---|---|---|",
        ]

        for label in LABELS:
            c = report["per_class"][label]
            lines.append(
                f"| {label} | {c['precision']:.3f} | {c['recall']:.3f}"
                f" | {c['f1']:.3f} | {c['support']} |"
            )

        lines += ["", _confusion_table(report["confusion_matrix"]), "", "### Misclassified", ""]

        wrong = [
            (item, predicted)
            for item, predicted in zip(dataset, result["predictions"])
            if item["label"] != predicted
        ]

        if not wrong:
            lines.append("None.")

        for item, predicted in wrong:
            lines.append(
                f"- \"{item['text']}\" — labeled **{item['label']}**, predicted **{predicted}**"
            )

    return "\n".join(lines) + "\n"


def main(
    argv: list[str] | None = None,
    scorer_factory: Callable[[str], Scorer] = get_scorer,
) -> None:
    parser = argparse.ArgumentParser(description="Evaluate sentiment scorers.")
    parser.add_argument("--scorers", default="vader,lexicon")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    dataset = load_dataset(args.dataset)

    try:
        results = evaluate(dataset, args.scorers.split(","), scorer_factory)
    except ValueError as error:
        parser.error(str(error))

    for name, result in results.items():
        report = result["report"]
        print(f"{name}: accuracy={report['accuracy']:.3f} macro_f1={report['macro_f1']:.3f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_report(dataset, results, date.today()), encoding="utf-8"
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
