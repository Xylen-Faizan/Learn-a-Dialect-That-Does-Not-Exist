from pathlib import Path
from src.evidence_engine import EvidenceEngine
from src.models import DecisionEnum
from src.pipeline import Nadi9Pipeline
from src.replanner import SelectiveReplanner


def test_selective_replanning():
    data_dir = Path("data")
    output_dir = Path("sample_run")
    pipeline = Nadi9Pipeline(data_dir, output_dir)

    initial_decisions = pipeline.run()
    transcript_lines = pipeline.load_transcript()

    replanner = SelectiveReplanner(pipeline.translator, pipeline.verifier)

    # Simulate linguist resolving negation rule
    updated_decisions, reprocessed_ids = replanner.apply_rule_update(
        target_rule_id="grammar:negation-1",
        current_decisions=initial_decisions,
        transcript_lines=transcript_lines,
    )

    # S004 contains negation ("did not see")
    assert "S004" in reprocessed_ids
    # S002 does NOT contain negation
    assert "S002" not in reprocessed_ids
    # Asserts selective execution rather than reprocessing the full batch
    assert len(reprocessed_ids) < len(initial_decisions)
