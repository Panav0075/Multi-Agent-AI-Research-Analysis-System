import re
from .base import BaseAgent
from ..schemas import TraceEvent


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class AnalysisAgent(BaseAgent):
    name = "analyst"

    def run(self, state):
        findings = []

        for evidence in state.evidence:
            sentences = [
                s.strip()
                for s in SENTENCE_SPLIT.split(evidence.passage)
                if len(s.split()) >= 5
            ]
            for sentence in sentences[:2]:
                findings.append(f"{sentence} [{evidence.source}]")

        state.findings = findings[:8]
        state.recommendation = self._recommend(state)

        state.trace.append(
            TraceEvent(
                agent=self.name,
                status="completed",
                summary=f"Produced {len(state.findings)} findings",
                details={"recommendation": state.recommendation},
            )
        )
        return state

    def _recommend(self, state):
        request = state.request.lower()
        evidence_text = " ".join(item.passage.lower() for item in state.evidence)

        if (
            ("response" in request or "first-response" in request)
            and ("documentation" in request or "self-service" in request)
        ):
            if "repeat-contact" in evidence_text and "sla target" in evidence_text:
                return (
                    "Prioritize self-service documentation coverage first while "
                    "continuing to monitor first-response time."
                )

        if "onboarding" in request and ("automation" in request or "automate" in request):
            return (
                "Prioritize automation for repetitive onboarding steps, while "
                "keeping human review for exceptions and access decisions."
            )

        if "automation" in request and ("ticket" in request or "support" in request):
            return (
                "Start with high-volume, low-risk support categories where the "
                "available evidence shows repeatable resolution patterns."
            )

        if state.evidence:
            return (
                "Use the highest-ranked evidence as the basis for the decision, "
                "and validate the recommendation against the cited sources."
            )

        return "There is not enough evidence to make a supported recommendation."
