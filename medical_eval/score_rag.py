#!/usr/bin/env python3
"""Run LightRAG's existing RAGAS evaluator for a medical QA dataset."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the built-in LightRAG RAGAS evaluator."
    )
    parser.add_argument("--dataset", required=True, help="Medical QA dataset JSON.")
    parser.add_argument(
        "--ragendpoint",
        default="http://localhost:9621",
        help="LightRAG server URL.",
    )
    args = parser.parse_args()

    evaluator = Path("lightrag/evaluation/eval_rag_quality.py")
    command = [
        sys.executable,
        str(evaluator),
        "--dataset",
        args.dataset,
        "--ragendpoint",
        args.ragendpoint,
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
