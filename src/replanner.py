from typing import List, Tuple
from src.models import SubtitleDecision, TranscriptLine
from src.translator import Translator
from src.verifier import IndependentVerifier


class SelectiveReplanner:
    """
    Reruns ONLY decisions dependent on an altered rule or term.
    """

    def __init__(self, translator: Translator, verifier: IndependentVerifier):
        self.translator = translator
        self.verifier = verifier

    def apply_rule_update(
        self,
        target_rule_id: str,
        current_decisions: List[SubtitleDecision],
        transcript_lines: List[TranscriptLine],
    ) -> Tuple[List[SubtitleDecision], List[str]]:
        updated_decisions = []
        reprocessed_ids = []

        line_map = {l.line_id: l for l in transcript_lines}

        for dec in current_decisions:
            if target_rule_id in dec.affected_rule_ids:
                # Reprocess only affected line
                line = line_map[dec.subtitle_id]
                nadi_text, ev, assump, aff_rules = self.translator.translate_line(line)
                new_decision = self.verifier.verify(
                    line, nadi_text, ev, assump, aff_rules
                )
                updated_decisions.append(new_decision)
                reprocessed_ids.append(dec.subtitle_id)
            else:
                updated_decisions.append(dec)

        return updated_decisions, reprocessed_ids
