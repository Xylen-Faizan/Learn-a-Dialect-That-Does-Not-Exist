import pytest
from pathlib import Path
from src.evidence_engine import EvidenceEngine
from src.models import DecisionEnum, TranscriptLine
from src.verifier import IndependentVerifier


def test_tool_failure_graceful_recovery():
    engine = EvidenceEngine(Path("data"))
    verifier = IndependentVerifier(engine)

    line = TranscriptLine(
        line_id="T04",
        start_time="00:00:00,000",
        end_time="00:00:02,000",
        speaker="Speaker_D",
        source_text="System failure simulation",
        context="Corrupted generation",
    )

    try:
        # Simulate broken translation token failure
        raw_output = "[UNSUPPORTED:corrupted_tool_failure]"
        decision = verifier.verify(line, raw_output, [], [], [])
        assert decision.decision == DecisionEnum.HUMAN_REVIEW
    except Exception as exc:
        pytest.fail(f"Pipeline crashed instead of gracefully escalating: {exc}")
