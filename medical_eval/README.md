# Medical Evaluation Toolkit

This directory adds lightweight evaluation helpers for checking LightRAG on
de-identified patient medical documents.

## What It Covers

- Extraction quality: entity and relation precision, recall, and F1.
- RAG answer quality: delegates to LightRAG's built-in RAGAS evaluator.
- Model comparison: combines extraction and RAGAS results into one CSV row per model.

## Gold Extraction Format

Create a gold JSON file:

```json
{
  "entities": [
    {"text": "Type 2 diabetes", "type": "Diagnosis"},
    {"text": "Metformin", "type": "Medication"}
  ],
  "relations": [
    {"source": "Metformin", "target": "Type 2 diabetes", "type": "treats"}
  ]
}
```

Predictions can use the same JSON format, or a LightRAG GraphML file such as:

```text
rag_storage/graph_chunk_entity_relation.graphml
```

Run extraction scoring:

```bash
python -m medical_eval.score_extraction \
  --gold medical_eval/gold/extraction_gold.json \
  --predicted rag_storage/graph_chunk_entity_relation.graphml \
  --output medical_eval/results/extraction_gemini.json
```

## RAG QA Dataset Format

Use the same format as `lightrag/evaluation/sample_dataset.json`:

```json
{
  "test_cases": [
    {
      "question": "What diagnosis is documented for the patient?",
      "ground_truth": "The patient is documented as having Type 2 diabetes.",
      "project": "medical_eval"
    }
  ]
}
```

Run RAGAS scoring while `lightrag-server` is running:

```bash
python -m medical_eval.score_rag \
  --dataset medical_eval/datasets/qa_dataset.json \
  --ragendpoint http://localhost:9621
```

The underlying LightRAG evaluator writes CSV and JSON files under:

```text
lightrag/evaluation/results/
```

## Model Comparison

Append one model result:

```bash
python -m medical_eval.run_model_eval \
  --model gemini-3.1-flash-lite-preview__gemini-embedding-001 \
  --extraction-result medical_eval/results/extraction_gemini.json \
  --ragas-result lightrag/evaluation/results/results_YYYYMMDD_HHMMSS.csv \
  --document-count 20 \
  --duration-seconds 1800 \
  --failed-documents 0 \
  --output medical_eval/results/model_comparison.csv
```

Repeat the same command for each model. The output CSV is the discussion table.

## Recommended First Pass

- 10-20 de-identified patient documents.
- 30-50 QA pairs with evidence-backed ground truth.
- One LightRAG workspace per model pair.
- Keep `MAX_ASYNC=1` and `EMBEDDING_FUNC_MAX_ASYNC=1` for quota-limited APIs.
