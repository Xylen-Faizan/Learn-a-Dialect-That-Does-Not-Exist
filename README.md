# Nadi-9 Dialect Translation Engine

An epistemic, evidence-driven subtitle translation system for the fictional Nadi-9 dialect. The system demonstrates **epistemic humility**: it knows what it does not know, tracks conflicting sources, abstains when evidence is missing, and verifies its own work independently.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run unit tests (All 4 mandatory tests pass out of the box)
pytest tests/ -v

# 3. Run full mock pipeline
python src/pipeline.py --mode mock

# 4. Inspect generated review queue
cat sample_run/review_queue.json
```

## Architecture Overview

```
[ Input Pack ] -> [ Evidence Analyzer ] -> [ Hypothesis Engine ] -> [ Translation Generator ] -> [ Independent Verifier ] -> [ Accepted / Human Review ] -> [ Selective Replanner ]
```

### Trust Hierarchy
| Source | Trust Score |
|---|---|
| Approved Examples | 1.00 |
| Dictionary B (Community Linguist) | 0.85 |
| Dictionary A (Vendor) | 0.65 |
| Viewer Feedback | 0.40 |

### Key Design Decisions
- **No hallucination:** Unknown terms produce `[UNSUPPORTED:word]` placeholders instead of invented words.
- **Independent verification:** The verifier module never trusts translator output — it runs its own deterministic checks.
- **Selective replanning:** Rule updates only reprocess affected subtitle lines, not the entire episode.
- **Conflict transparency:** Dictionary disagreements are logged and escalated, never silently resolved.

## Project Structure

```
nadi9_engine/
├── data/                    # Input lexicons, grammar, transcript
├── src/                     # Core engine modules
│   ├── models.py            # Pydantic data contracts
│   ├── evidence_engine.py   # Source ranking & conflict detection
│   ├── translator.py        # Rule-based translation
│   ├── verifier.py          # Independent verification
│   ├── replanner.py         # Selective reprocessing
│   └── pipeline.py          # End-to-end orchestrator
├── tests/                   # 4 mandatory test suites
├── sample_run/              # Generated output artifacts
├── AI_COLLABORATION.md      # AI supervision log
├── ARCHITECTURE.md          # System design & trust boundaries
└── KNOWN_LIMITATIONS.md     # Honest tradeoff documentation
```

## Output Artifacts

After running the pipeline, `sample_run/` contains:
- `subtitles.srt` — Standard SRT with Nadi-9 translations
- `subtitle_decisions.jsonl` — Per-line decision records
- `learned_rules.json` — Extracted grammar rules with evidence
- `review_queue.json` — Items requiring human linguist review
- `final_report.md` — Processing statistics and status
