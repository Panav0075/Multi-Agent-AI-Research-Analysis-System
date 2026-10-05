from .base import BaseAgent
from ..schemas import TraceEvent


class WriterAgent(BaseAgent):
    name = "writer"

    def run(self, state):
        if not state.evidence:
            state.final_answer = (
                "I could not find enough evidence in the available knowledge base "
                "to answer this request reliably."
            )
        else:
            source_names = []
            for evidence in state.evidence:
                if evidence.source not in source_names:
                    source_names.append(evidence.source)

            findings = "\n".join(
                f"- {finding}" for finding in state.findings[:4]
            )

            sources = "\n".join(f"- {source}" for source in source_names)

            state.final_answer = (
                f"Recommendation\n\n"
                f"{state.recommendation}\n\n"
                f"Key findings\n{findings}\n\n"
                f"Sources\n{sources}"
            )

        state.trace.append(
            TraceEvent(
                agent=self.name,
                status="completed",
                summary="Created the final source-backed response",
                details={"answer_length": len(state.final_answer)},
            )
        )
        return state
