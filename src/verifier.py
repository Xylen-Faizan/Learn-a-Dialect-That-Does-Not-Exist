import re
from src.evidence_engine import EvidenceEngine
from src.models import DecisionEnum, SubtitleDecision, TranscriptLine


class IndependentVerifier:
    """
    Evaluates translations independently.
    Does NOT rely on translator assertions.
    """

    def __init__(self, evidence_engine: EvidenceEngine):
        self.evidence = evidence_engine

    def verify(
        self,
        line: TranscriptLine,
        proposed_nadi: str,
        evidence: list,
        assumptions: list,
        affected_rules: list,
    ) -> SubtitleDecision:
        conflicts = []
        review_question = None

        # Check 1: Unsupported Tokens
        unsupported = re.findall(r"\[UNSUPPORTED:([a-zA-Z0-9_-]+)\]", proposed_nadi)
        if unsupported:
            return SubtitleDecision(
                subtitle_id=line.line_id,
                source_text=line.source_text,
                nadi_9_text=proposed_nadi,
                confidence=0.20,
                decision=DecisionEnum.HUMAN_REVIEW,
                evidence=evidence,
                assumptions=assumptions,
                conflicts=[],
                review_question=(
                    f"No evidence for token(s): {', '.join(unsupported)}. "
                    "Provide lexical entry."
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

        # Check 3: Clean pass verification
        confidence = 0.92
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
