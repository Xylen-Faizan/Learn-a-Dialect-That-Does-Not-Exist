# AI Collaboration & Verification Log

In compliance with the hiring assignment evaluation guidelines, this log documents how AI tools (Claude 3.5 Sonnet / Codex) were supervised, validated, and actively corrected.

## 1. Task: Kinship Morphology Induction
- **AI Proposal:** The LLM suggested that elder kinship suffixes were uniform across all speaker relationships, proposing `tal-vok` for all familial lines.
- **Verification:** Checked against `data/dictionary_a.json` (vendor source) and `data/dictionary_b.json` (community linguist). 
- **Intervention:** Discovered a 100% lexical collision between `mor-vok` and `tal-vok`. Rejected the LLM's unified rule and instituted an explicit conflict logger requiring human review.

## 2. Task: Self-Verification vs Independent Verifier
- **AI Proposal:** Generated an agent prompt asking the translator LLM to rate its own confidence score from 0.0 to 1.0.
- **Verification:** Identified that the model assigned 0.95 confidence even to sentences with unsupported vocabulary.
- **Intervention:** Completely discarded LLM self-verification. Built `src/verifier.py` with deterministic regex checks (`[UNSUPPORTED:...]`) and independent schema validation.

## 3. Tool Budget Management
- Implemented a deterministic mock mode (`src/pipeline.py --mode mock`) to allow evaluators to inspect end-to-end functionality within the 25-call budget ceiling.
