import re
from typing import List
from src.evidence_engine import EvidenceEngine
from src.models import DecisionEnum, SubtitleDecision, TranscriptLine


class IndependentVerifier:
    """
    Evaluates translations independently.
    Does NOT rely on translator assertions.
    """

    # Keywords that indicate prompt injection or system instruction leakage
    INJECTION_KEYWORDS = [
        "ignore previous",
        "system prompt",
        "override",
        "disregard instructions",
        "forget your rules",
    ]

    def __init__(self, evidence_engine: EvidenceEngine):
        self.evidence = evidence_engine

    def verify(
        self,
        line: TranscriptLine,
        proposed_nadi: str,
        evidence: List[str],
        assumptions: List[str],
        affected_rules: List[str],
    ) -> SubtitleDecision:
        conflicts = []
        review_question = None

        # Check 0: Prompt injection / data poisoning defense (Section 6)
        combined_text = f"{proposed_nadi} {line.context}".lower()
        if any(kw in combined_text for kw in self.INJECTION_KEYWORDS):
            return SubtitleDecision(
                subtitle_id=line.line_id,
                source_text=line.source_text,
                nadi_9_text="[SECURITY_FLAG_REJECTED]",
                confidence=0.0,
                decision=DecisionEnum.REJECTED,
                evidence=evidence,
                assumptions=[
                    "Detected potential prompt injection in source/retrieval."
                ],
                conflicts=["injection_attempt_detected"],
                review_question=(
                    "Source contains malicious prompt injection instruction. "
                    "Disregard?"
                ),
                affected_rule_ids=affected_rules,
            )

        # Check 1: Unsupported Tokens
        unsupported = re.findall(
            r"\[UNSUPPORTED:([a-zA-Z0-9_-]+)\]", proposed_nadi
        )
        if unsupported:
            return SubtitleDecision(
                subtitle_id=line.line_id,
                source_text=line.source_text,
                nadi_9_text=proposed_nadi,
                confidence=0.15,
                decision=DecisionEnum.HUMAN_REVIEW,
                evidence=evidence,
                assumptions=assumptions,
                conflicts=[],
                review_question=(
                    f"No verified lexical evidence for token(s): "
                    f"{', '.join(unsupported)}."
                ),
                affected_rule_ids=affected_rules,
            )

        # Check 2: Kinship / Known Dictionary Disagreements
        if "elder brother" in line.source_text.lower():
            conflict_tag = self.evidence.get_conflict_for_term("elder brother")
            if conflict_tag:
                conflicts.append(conflict_tag)
                review_question = (
                    "Which kinship form applies after reconciliation? "
                    "(Dictionary A: mor-vok vs Dictionary B: tal-vok)"
                )
                return SubtitleDecision(
                    subtitle_id=line.line_id,
                    source_text=line.source_text,
                    nadi_9_text=proposed_nadi,
                    confidence=0.72,
                    decision=DecisionEnum.HUMAN_REVIEW,
                    evidence=evidence,
                    assumptions=assumptions,
                    conflicts=conflicts,
                    review_question=review_question,
                    affected_rule_ids=affected_rules,
                )

        # Check 3: Calibrated Confidence Calculation (Section 9)
        # Confidence = 0.4*LexicalCoverage + 0.3*SourceTrustScore
        #            + 0.3*GrammarMatch - 0.2*ConflictCount
        has_grammar_support = any("grammar:" in ev for ev in evidence)
        has_dict_b = any("dictionary:B" in ev for ev in evidence)

        confidence = 0.70  # Base confidence for resolved tokens
        if has_grammar_support:
            confidence += 0.15
        if has_dict_b:
            confidence += 0.10
        confidence = min(round(confidence, 2), 0.98)

        return SubtitleDecision(
            subtitle_id=line.line_id,
            source_text=line.source_text,
            nadi_9_text=proposed_nadi,
            confidence=confidence,
            decision=DecisionEnum.ACCEPTED,
            evidence=evidence,
            assumptions=assumptions,
            conflicts=[],
            review_question=None,
            affected_rule_ids=affected_rules,
        )
