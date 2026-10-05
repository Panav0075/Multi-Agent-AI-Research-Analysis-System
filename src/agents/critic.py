from .base import BaseAgent
from ..schemas import TraceEvent


class CriticAgent(BaseAgent):
    name = "critic"

    def run(self, state):
        reasons = []

        if not state.evidence:
            reasons.append("No evidence was retrieved.")

        if len(state.evidence) < 2:
            reasons.append("The recommendation is supported by fewer than two sources.")

        if not state.findings:
            reasons.append("No structured findings were produced.")

        if "not enough evidence" in state.recommendation.lower():
            reasons.append("The analyst reported insufficient evidence.")

        approved = len(reasons) == 0

        state.critique = {
            "approved": approved,
            "reasons": reasons,
            "research_query": state.request if not approved else "",
        }

        state.trace.append(
            TraceEvent(
                agent=self.name,
                status="approved" if approved else "revision_requested",
                summary=(
                    "Evidence and analysis passed verification"
                    if approved
                    else "; ".join(reasons)
                ),
                details=state.critique.copy(),
            )
        )
        return state
