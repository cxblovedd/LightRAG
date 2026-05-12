#!/usr/bin/env python3
"""Build a compact model comparison row from extraction and RAGAS results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


SUMMARY_FIELDS = [
    "model",
    "entity_precision",
    "entity_recall",
    "entity_f1",
    "relation_precision",
    "relation_recall",
    "relation_f1",
    "faithfulness",
    "answer_relevance",
    "context_recall",
    "context_precision",
    "ragas_score",
    "document_count",
    "duration_seconds",
    "failed_documents",
    "notes",
]


def _average_csv_column(rows: list[dict[str, str]], column: str) -> float:
    values: list[float] = []
    for row in rows:
        value = row.get(column, "")
        if value and value.upper() != "N/A":
            values.append(float(value))
    return round(sum(values) / len(values), 4) if values else 0.0


def _read_ragas_summary(path: Path | None) -> dict[str, float]:
    if path is None:
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {
        "faithfulness": _average_csv_column(rows, "faithfulness"),
        "answer_relevance": _average_csv_column(rows, "answer_relevance"),
        "context_recall": _average_csv_column(rows, "context_recall"),
        "context_precision": _average_csv_column(rows, "context_precision"),
        "ragas_score": _average_csv_column(rows, "ragas_score"),
    }


def _read_extraction_summary(path: Path | None) -> dict[str, float]:
    if path is None:
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    entities = data.get("entities", {})
    relations = data.get("relations", {})
    return {
        "entity_precision": entities.get("precision", 0.0),
        "entity_recall": entities.get("recall", 0.0),
        "entity_f1": entities.get("f1", 0.0),
        "relation_precision": relations.get("precision", 0.0),
        "relation_recall": relations.get("recall", 0.0),
        "relation_f1": relations.get("f1", 0.0),
    }


def build_model_summary(
    model_name: str,
    extraction_result: Path | None = None,
    ragas_result: Path | None = None,
    document_count: int | None = None,
    duration_seconds: float | None = None,
    failed_documents: int | None = None,
    notes: str = "",
) -> dict[str, Any]:
    summary: dict[str, Any] = {field: "" for field in SUMMARY_FIELDS}
    summary["model"] = model_name
    summary.update(_read_extraction_summary(extraction_result))
    summary.update(_read_ragas_summary(ragas_result))
    summary["document_count"] = "" if document_count is None else document_count
    summary["duration_seconds"] = "" if duration_seconds is None else duration_seconds
    summary["failed_documents"] = "" if failed_documents is None else failed_documents
    summary["notes"] = notes
    return summary


def append_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({field: summary.get(field, "") for field in SUMMARY_FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append one model result to a comparison CSV."
    )
    parser.add_argument("--model", required=True, help="Model or model pair name.")
    parser.add_argument(
        "--extraction-result",
        type=Path,
        help="Output JSON from score_extraction.py.",
    )
    parser.add_argument(
        "--ragas-result",
        type=Path,
        help="CSV output from LightRAG RAGAS evaluator.",
    )
    parser.add_argument("--document-count", type=int)
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--failed-documents", type=int)
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("medical_eval/results/model_comparison.csv"),
        help="Comparison CSV path.",
    )
    args = parser.parse_args()

    summary = build_model_summary(
        model_name=args.model,
        extraction_result=args.extraction_result,
        ragas_result=args.ragas_result,
        document_count=args.document_count,
        duration_seconds=args.duration_seconds,
        failed_documents=args.failed_documents,
        notes=args.notes,
    )
    append_summary(args.output, summary)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
