from pathlib import Path
from src.evidence_engine import EvidenceEngine
from src.models import DecisionEnum, TranscriptLine
from src.translator import Translator
from src.verifier import IndependentVerifier


def test_dictionary_conflict_escalation():
    engine = EvidenceEngine(Path("data"))
    translator = Translator(engine)
    verifier = IndependentVerifier(engine)

    line = TranscriptLine(
        line_id="T01",
        start_time="00:00:00,000",
        end_time="00:00:02,000",
        speaker="Speaker_A",
        source_text="You came back, elder brother?",
        context="Testing conflict handling",
    )

    nadi, ev, assump, rules = translator.translate_line(line)
    decision = verifier.verify(line, nadi, ev, assump, rules)

    assert decision.decision == DecisionEnum.HUMAN_REVIEW
    assert len(decision.conflicts) > 0
    assert "dictionary:A:elder brother vs dictionary:B:elder brother" in decision.conflicts
    assert decision.review_question is not None
    assert decision.confidence < 0.80
