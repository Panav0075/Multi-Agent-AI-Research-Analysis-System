from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class Evidence:
    source: str
    title: str
    passage: str
    score: float


@dataclass
class TraceEvent:
    agent: str
    status: str
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    request: str
    plan: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Evidence] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    recommendation: str = ""
    critique: Dict[str, Any] = field(default_factory=dict)
    final_answer: str = ""
    retry_count: int = 0
    trace: List[TraceEvent] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)
