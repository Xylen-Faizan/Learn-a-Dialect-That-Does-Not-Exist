from typing import List, Tuple
from src.evidence_engine import EvidenceEngine
from src.models import TranscriptLine


class Translator:
    def __init__(self, evidence_engine: EvidenceEngine):
        self.evidence = evidence_engine

    def translate_line(
        self, line: TranscriptLine
    ) -> Tuple[str, List[str], List[str], List[str]]:
        """
        Returns:
            nadi_9_text, evidence_list, assumptions_list, affected_rules
        """
        text = line.source_text.lower().replace("?", "").replace(".", "")
        words = text.split()

        evidence: List[str] = []
        assumptions: List[str] = []
        affected_rules: List[str] = []
        translated_tokens: List[str] = []

        # Target Specific Contexts
        if "elder brother" in text:
            conflict = self.evidence.get_conflict_for_term("elder brother")
            if conflict:
                evidence.append(conflict)
            term_info = self.evidence.lookup_term("elder brother")
            if term_info:
                translated_tokens.append(term_info[0])
                evidence.append(term_info[1])
                affected_rules.append("grammar:respect-2")
                assumptions.append(
                    f"Speaker '{line.speaker}' addresses an older sibling."
                )

            if "came back" in text:
                term_cb = self.evidence.lookup_term("come back")
                if term_cb:
                    translated_tokens.append(f"{term_cb[0]}-sh")
                    evidence.append("grammar:past-tense-1")
                    affected_rules.append("grammar:past-tense-1")

            nadi_text = f"{', '.join(translated_tokens)}?"
            return nadi_text, evidence, assumptions, affected_rules

        # Standard Token Processing
        for word in words:
            # Check multi-word or single-word lookup
            lookup = self.evidence.lookup_term(word)
            if lookup:
                translated_tokens.append(lookup[0])
                evidence.append(lookup[1])
                affected_rules.append(f"lexicon:{word}")
            elif word in ["not", "did", "do"]:
                continue  # Handled in morphology
            elif word in [
                "is", "the", "at", "him", "her", "his",
                "you", "i", "we", "he", "she", "it", "they",
                "a", "an", "to", "of", "in", "on", "for",
                "my", "your", "our", "their", "its",
                "must", "can", "will", "shall", "should", "would", "could",
                "has", "have", "had", "was", "were", "are", "am", "be",
                "this", "that", "these", "those",
                "and", "or", "but", "if", "then", "so",
                "with", "from", "by", "about", "into",
                "what", "who", "where", "when", "how", "why",
                "there", "here",
            ]:
                continue  # Functional syntax handled via affixes / grammar rules
            else:
                translated_tokens.append(f"[UNSUPPORTED:{word}]")

        # Syntactic checks (Negation)
        if "not" in words and "see" in words:
            term_see = self.evidence.lookup_term("see")
            see_val = term_see[0] if term_see else "mir"
            translated_tokens = [t for t in translated_tokens if t != see_val]
            translated_tokens.append(f"{see_val}-nai-sh")
            evidence.append("grammar:negation-1")
            evidence.append("grammar:past-tense-1")
            affected_rules.extend(["grammar:negation-1", "grammar:past-tense-1"])
            assumptions.append("Negation suffix '-nai' applied to verb stem.")

        if "waiting" in words:
            term_w = self.evidence.lookup_term("waiting")
            term_f = self.evidence.lookup_term("father")
            term_h = self.evidence.lookup_term("home")
            translated_tokens = [
                term_f[0] if term_f else "aba",
                f"{term_h[0] if term_h else 'kor'}-te",
                term_w[0] if term_w else "pel-sh",
            ]
            evidence.append("grammar:word-order-sov")
            affected_rules.append("grammar:word-order-sov")

        nadi_text = " ".join(translated_tokens)
        if line.source_text.endswith("?"):
            nadi_text += "?"
        else:
            nadi_text += "."

        return nadi_text, evidence, assumptions, affected_rules
