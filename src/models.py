from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class DecisionEnum(str, Enum):
    ACCEPTED = "ACCEPTED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    REJECTED = "REJECTED"


class SubtitleDecision(BaseModel):
    subtitle_id: str
    source_text: str
    nadi_9_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    decision: DecisionEnum
    evidence: List[str]
    assumptions: List[str]
    conflicts: List[str] = []
    review_question: Optional[str] = None
    affected_rule_ids: List[str] = []


class TranscriptLine(BaseModel):
    line_id: str
    start_time: str
    end_time: str
    speaker: str
    source_text: str
    context: str
