from pathlib import Path
from src.evidence_engine import EvidenceEngine
from src.models import DecisionEnum, TranscriptLine
from src.translator import Translator
from src.verifier import IndependentVerifier


def test_unsupported_term_abstention():
    engine = EvidenceEngine(Path("data"))
    translator = Translator(engine)
    verifier = IndependentVerifier(engine)

    line = TranscriptLine(
        line_id="T02",
        start_time="00:00:00,000",
        end_time="00:00:02,000",
        speaker="Speaker_B",
        source_text="Did you uncover the secret?",
        context="Testing missing vocabulary",
    )

    nadi, ev, assump, rules = translator.translate_line(line)
    decision = verifier.verify(line, nadi, ev, assump, rules)

    assert "[UNSUPPORTED:secret]" in decision.nadi_9_text
    assert decision.decision == DecisionEnum.HUMAN_REVIEW
    assert decision.confidence <= 0.20
    assert "secret" in decision.review_question
