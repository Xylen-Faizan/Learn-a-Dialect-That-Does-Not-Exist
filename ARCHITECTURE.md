# Nadi-9 Agent Architecture & Trust Boundaries

## 1. System Topology
The system separates generation from verification:
- **Evidence Engine:** Computes source trust rank (`approved_examples`: 1.0 > `dictionary_b`: 0.85 > `dictionary_a`: 0.65). Flags lexical disagreements into an active conflict registry.
- **Translator Module:** Generates candidate Nadi-9 translations, tagging non-lexicon tokens with explicit markers.
- **Independent Verifier:** Evaluates the candidate against known constraints. Hallucinated tokens or unresolved conflicts are routed directly to `review_queue.json`.
- **Selective Replanner:** Maps decisions to `affected_rule_ids`. When a rule changes, only dependents are recalculated.

## 2. Trust Boundaries
- **Untrusted:** Generative text output from models.
- **Trusted:** Source precedence rules, regex lexicon matches, and linguist review decisions.

## 3. Confidence Formula
```
Confidence = 0.4 * LexicalCoverage + 0.3 * SourceTrustScore + 0.3 * GrammarMatch - (0.2 * ConflictCount)
```

## 4. Call Budget Enforcement
The pipeline enforces a strict budget of 25 LLM calls and 50 tool calls. In mock mode, zero LLM calls are consumed. In live mode, a counter middleware tracks and aborts execution if the ceiling is exceeded.
