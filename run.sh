#!/usr/bin/env bash
set -e

echo "=== Installing Dependencies ==="
pip install -r requirements.txt

echo "=== Running Automated Test Suite ==="
pytest tests/ -v

echo "=== Executing Pipeline (Mock Mode) ==="
python src/pipeline.py --mode mock --output_dir sample_run

echo "=== Execution Summary ==="
cat sample_run/final_report.md
