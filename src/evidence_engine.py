import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class EvidenceEngine:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.dict_a = self._load_json(data_dir / "dictionary_a.json")
        self.dict_b = self._load_json(data_dir / "dictionary_b.json")
        self.grammar = self._load_json(data_dir / "grammar_rules.json")
        self.examples = self._load_json(data_dir / "approved_examples.json")
        self.conflicts: Dict[str, Dict[str, Any]] = {}
        self.active_lexicon: Dict[str, Tuple[str, str, float]] = {}
        self._build_lexicon_and_detect_conflicts()

    def _load_json(self, path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_lexicon_and_detect_conflicts(self):
        entries_a = self.dict_a.get("entries", {})
        entries_b = self.dict_b.get("entries", {})
        all_keys = set(entries_a.keys()).union(set(entries_b.keys()))

        for key in all_keys:
            val_a = entries_a.get(key)
            val_b = entries_b.get(key)

            if val_a and val_b and val_a != val_b:
                # Register conflict
                self.conflicts[key] = {
                    "source_a": f"dictionary:A:{val_a}",
                    "source_b": f"dictionary:B:{val_b}",
                    "conflict_tag": f"dictionary:A:{key} vs dictionary:B:{key}",
                }
                # Precedence: Dict B takes tentative operational priority
                self.active_lexicon[key] = (val_b, "dictionary:B", 0.85)
            elif val_b:
                self.active_lexicon[key] = (val_b, "dictionary:B", 0.85)
            elif val_a:
                self.active_lexicon[key] = (val_a, "dictionary:A", 0.65)

    def lookup_term(self, term: str) -> Optional[Tuple[str, str, float]]:
        cleaned = term.lower().strip()
        return self.active_lexicon.get(cleaned)

    def get_conflict_for_term(self, term: str) -> Optional[str]:
        cleaned = term.lower().strip()
        if cleaned in self.conflicts:
            return self.conflicts[cleaned]["conflict_tag"]
        return None
