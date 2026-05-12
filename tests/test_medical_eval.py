import csv
import json
from pathlib import Path

from medical_eval.run_model_eval import build_model_summary
from medical_eval.score_extraction import (
    load_predictions_from_graphml,
    score_extraction,
)


def test_score_extraction_counts_entities_and_relations():
    gold = {
        "entities": [
            {"text": "Type 2 diabetes", "type": "Diagnosis"},
            {"text": "Metformin", "type": "Medication"},
        ],
        "relations": [
            {
                "source": "Metformin",
                "target": "Type 2 diabetes",
                "type": "treats",
            }
        ],
    }
    predicted = {
        "entities": [
            {"text": "type 2 diabetes", "type": "Diagnosis"},
            {"text": "Aspirin", "type": "Medication"},
        ],
        "relations": [
            {
                "source": "Metformin",
                "target": "Type 2 diabetes",
                "type": "treats",
            },
            {
                "source": "Aspirin",
                "target": "Headache",
                "type": "treats",
            },
        ],
    }

    report = score_extraction(gold, predicted)

    assert report["entities"]["true_positive"] == 1
    assert report["entities"]["false_positive"] == 1
    assert report["entities"]["false_negative"] == 1
    assert report["entities"]["precision"] == 0.5
    assert report["entities"]["recall"] == 0.5
    assert report["entities"]["f1"] == 0.5
    assert report["relations"]["true_positive"] == 1
    assert report["relations"]["false_positive"] == 1
    assert report["relations"]["false_negative"] == 0


def test_load_predictions_from_graphml(tmp_path: Path):
    graphml = tmp_path / "graph.graphml"
    graphml.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d0" for="node" attr.name="entity_type" attr.type="string"/>
  <key id="d1" for="edge" attr.name="keywords" attr.type="string"/>
  <graph edgedefault="undirected">
    <node id="Metformin"><data key="d0">Medication</data></node>
    <node id="Type 2 diabetes"><data key="d0">Diagnosis</data></node>
    <edge source="Metformin" target="Type 2 diabetes">
      <data key="d1">treats</data>
    </edge>
  </graph>
</graphml>
""",
        encoding="utf-8",
    )

    data = load_predictions_from_graphml(graphml)

    assert {"text": "Metformin", "type": "Medication"} in data["entities"]
    assert {
        "source": "Metformin",
        "target": "Type 2 diabetes",
        "type": "treats",
    } in data["relations"]


def test_build_model_summary_from_result_files(tmp_path: Path):
    extraction_result = tmp_path / "extraction.json"
    extraction_result.write_text(
        json.dumps(
            {
                "entities": {"precision": 0.8, "recall": 0.6, "f1": 0.6857},
                "relations": {"precision": 0.7, "recall": 0.5, "f1": 0.5833},
            }
        ),
        encoding="utf-8",
    )

    ragas_result = tmp_path / "ragas.csv"
    with ragas_result.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "faithfulness",
                "answer_relevance",
                "context_recall",
                "context_precision",
                "ragas_score",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "faithfulness": "0.9",
                "answer_relevance": "0.8",
                "context_recall": "0.7",
                "context_precision": "0.6",
                "ragas_score": "0.75",
            }
        )
        writer.writerow(
            {
                "faithfulness": "0.7",
                "answer_relevance": "0.6",
                "context_recall": "0.5",
                "context_precision": "0.4",
                "ragas_score": "0.55",
            }
        )

    summary = build_model_summary(
        model_name="gemini-test",
        extraction_result=extraction_result,
        ragas_result=ragas_result,
    )

    assert summary["model"] == "gemini-test"
    assert summary["entity_f1"] == 0.6857
    assert summary["relation_f1"] == 0.5833
    assert summary["faithfulness"] == 0.8
    assert summary["context_recall"] == 0.6
    assert summary["ragas_score"] == 0.65
