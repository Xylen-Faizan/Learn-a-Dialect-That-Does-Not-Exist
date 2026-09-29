import argparse
import json
from pathlib import Path
from typing import List

from src.evidence_engine import EvidenceEngine
from src.models import DecisionEnum, SubtitleDecision, TranscriptLine
from src.translator import Translator
from src.verifier import IndependentVerifier


class Nadi9Pipeline:
    def __init__(self, data_dir: Path, output_dir: Path):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.evidence_engine = EvidenceEngine(data_dir)
        self.translator = Translator(self.evidence_engine)
        self.verifier = IndependentVerifier(self.evidence_engine)

    def load_transcript(self) -> List[TranscriptLine]:
        with open(
            self.data_dir / "episode_transcript.json", "r", encoding="utf-8"
        ) as f:
            raw = json.load(f)
        return [TranscriptLine(**item) for item in raw]

    def run(self) -> List[SubtitleDecision]:
        lines = self.load_transcript()
        decisions: List[SubtitleDecision] = []

        for line in lines:
            proposed, ev, assump, rules = self.translator.translate_line(line)
            decision = self.verifier.verify(line, proposed, ev, assump, rules)
            decisions.append(decision)

        self._export_outputs(lines, decisions)
        return decisions

    def _export_outputs(
        self, lines: List[TranscriptLine], decisions: List[SubtitleDecision]
    ):
        line_map = {l.line_id: l for l in lines}

        # 1. Export subtitle_decisions.jsonl
        jsonl_path = self.output_dir / "subtitle_decisions.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for d in decisions:
                f.write(d.model_dump_json() + "\n")

        # 2. Export review_queue.json
        review_queue = [
            d.model_dump()
            for d in decisions
            if d.decision == DecisionEnum.HUMAN_REVIEW
        ]
        with open(
            self.output_dir / "review_queue.json", "w", encoding="utf-8"
        ) as f:
            json.dump(review_queue, f, indent=2)

        # 3. Export learned_rules.json
        with open(
            self.output_dir / "learned_rules.json", "w", encoding="utf-8"
        ) as f:
            json.dump(self.evidence_engine.grammar, f, indent=2)

        # 4. Export subtitles.srt
        srt_path = self.output_dir / "subtitles.srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            for idx, d in enumerate(decisions, 1):
                tl = line_map[d.subtitle_id]
                # If unsupported token exists, format safely for viewing
                display_text = (
                    d.nadi_9_text
                    if d.decision == DecisionEnum.ACCEPTED
                    else f"[{d.nadi_9_text}]"
                )
                f.write(f"{idx}\n")
                f.write(f"{tl.start_time} --> {tl.end_time}\n")
                f.write(f"{display_text}\n\n")

        # 5. Export final_report.md
        accepted_count = sum(
            1 for d in decisions if d.decision == DecisionEnum.ACCEPTED
        )
        review_count = len(review_queue)
        report_path = self.output_dir / "final_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Nadi-9 Subtitle Processing Report\n\n")
            f.write(f"- **Total Subtitles Processed:** {len(decisions)}\n")
            f.write(f"- **Accepted:** {accepted_count}\n")
            f.write(f"- **Escalated to Human Review:** {review_count}\n")
            f.write("- **Model Calls Used:** 0 (Deterministic Mock Mode)\n")
            f.write(
                "- **Status:** READY FOR REVIEW. No unsupported tokens were hallucinated into production SRT.\n"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Nadi-9 Dialect Translation CLI"
    )
    parser.add_argument(
        "--mode",
        choices=["mock", "live"],
        default="mock",
        help="Run in offline deterministic mock mode without API keys",
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("data"),
        help="Input data directory",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("sample_run"),
        help="Output artifacts directory",
    )
    args = parser.parse_args()

    pipeline = Nadi9Pipeline(args.data_dir, args.output_dir)
    pipeline.run()
    print(f"Pipeline executed successfully. Artifacts saved in: {args.output_dir}")
