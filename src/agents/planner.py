from .base import BaseAgent
from ..schemas import TraceEvent


class PlannerAgent(BaseAgent):
    name = "planner"

    def run(self, state):
        request = state.request.strip()

        steps = [
            "identify the decision or information requested",
            "retrieve evidence from the available knowledge base",
            "compare the evidence and identify important trade-offs",
            "verify that the conclusion is supported by retrieved sources",
            "write a concise source-backed response",
        ]

        state.plan = {
            "objective": request,
            "steps": steps,
            "requires_research": True,
            "requires_verification": True,
        }

        state.trace.append(
            TraceEvent(
                agent=self.name,
                status="completed",
                summary=f"Created a {len(steps)}-step task plan",
                details={"steps": steps},
            )
        )
        return state
