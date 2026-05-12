#!/usr/bin/env python3
"""Score medical entity and relation extraction against a gold file."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def _normalize(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.strip().strip('"').strip("'").lower()
    return re.sub(r"\s+", " ", text)


def _entity_key(item: dict[str, Any]) -> tuple[str, str]:
    text = (
        item.get("text")
        or item.get("entity_name")
        or item.get("name")
        or item.get("id")
    )
    entity_type = item.get("type") or item.get("entity_type") or ""
    return (_normalize(text), _normalize(entity_type))


def _relation_key(item: dict[str, Any]) -> tuple[str, str, str]:
    source = item.get("source") or item.get("src") or item.get("src_id")
    target = item.get("target") or item.get("tgt") or item.get("tgt_id")
    rel_type = (
        item.get("type")
        or item.get("relation_type")
        or item.get("keywords")
        or ""
    )
    return (_normalize(source), _normalize(target), _normalize(rel_type))


def _metrics(
    gold_items: set[tuple[str, ...]],
    predicted_items: set[tuple[str, ...]],
) -> dict[str, Any]:
    true_positive = len(gold_items & predicted_items)
    false_positive = len(predicted_items - gold_items)
    false_negative = len(gold_items - predicted_items)

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    precision = (
        true_positive / precision_denominator if precision_denominator else 0.0
    )
    recall = true_positive / recall_denominator if recall_denominator else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def score_extraction(gold: dict[str, Any], predicted: dict[str, Any]) -> dict[str, Any]:
    gold_entities = {_entity_key(item) for item in gold.get("entities", [])}
    predicted_entities = {_entity_key(item) for item in predicted.get("entities", [])}
    gold_relations = {_relation_key(item) for item in gold.get("relations", [])}
    predicted_relations = {
        _relation_key(item) for item in predicted.get("relations", [])
    }

    return {
        "entities": _metrics(gold_entities, predicted_entities),
        "relations": _metrics(gold_relations, predicted_relations),
    }


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_predictions_from_graphml(path: Path) -> dict[str, list[dict[str, str]]]:
    tree = ET.parse(path)
    root = tree.getroot()
    namespace = {"g": "http://graphml.graphdrawing.org/xmlns"}

    key_names: dict[str, str] = {}
    for key in root.findall("g:key", namespace):
        key_id = key.attrib.get("id")
        attr_name = key.attrib.get("attr.name")
        if key_id and attr_name:
            key_names[key_id] = attr_name

    def data_map(element: ET.Element) -> dict[str, str]:
        values: dict[str, str] = {}
        for data in element.findall("g:data", namespace):
            key = data.attrib.get("key", "")
            name = key_names.get(key, key)
            values[name] = data.text or ""
        return values

    entities: list[dict[str, str]] = []
    for node in root.findall(".//g:node", namespace):
        values = data_map(node)
        entities.append(
            {
                "text": node.attrib.get("id", ""),
                "type": values.get("entity_type", values.get("type", "")),
            }
        )

    relations: list[dict[str, str]] = []
    for edge in root.findall(".//g:edge", namespace):
        values = data_map(edge)
        relations.append(
            {
                "source": edge.attrib.get("source", ""),
                "target": edge.attrib.get("target", ""),
                "type": values.get("relation_type", values.get("keywords", "")),
            }
        )

    return {"entities": entities, "relations": relations}


def load_predictions(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".graphml":
        return load_predictions_from_graphml(path)
    return _read_json(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score medical extraction against gold annotations."
    )
    parser.add_argument(
        "--gold",
        required=True,
        help="Gold JSON with entities and relations.",
    )
    parser.add_argument(
        "--predicted",
        required=True,
        help="Predicted JSON or LightRAG GraphML file.",
    )
    parser.add_argument("--output", help="Output JSON path.")
    args = parser.parse_args()

    report = score_extraction(
        _read_json(Path(args.gold)),
        load_predictions(Path(args.predicted)),
    )
    text = json.dumps(report, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
