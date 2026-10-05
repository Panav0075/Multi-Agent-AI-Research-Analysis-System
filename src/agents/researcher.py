from .base import BaseAgent
from ..schemas import Evidence, TraceEvent


class ResearchAgent(BaseAgent):
    name = "researcher"

    def __init__(self, search_tool, top_k=4):
        self.search_tool = search_tool
        self.top_k = top_k

    def run(self, state):
        results = self.search_tool.search(state.request, top_k=self.top_k)

        # On a critic-requested retry, include any explicit missing concepts.
        if state.retry_count > 0 and state.critique.get("research_query"):
            retry_results = self.search_tool.search(
                state.critique["research_query"],
                top_k=self.top_k,
            )
            by_source = {item["source"]: item for item in results}
            for item in retry_results:
                current = by_source.get(item["source"])
                if current is None or item["score"] > current["score"]:
                    by_source[item["source"]] = item
            results = sorted(
                by_source.values(),
                key=lambda item: item["score"],
                reverse=True,
            )[: self.top_k]

        state.evidence = [
            Evidence(
                source=item["source"],
                title=item["title"],
                passage=item["passage"],
                score=item["score"],
            )
            for item in results
        ]

        state.trace.append(
            TraceEvent(
                agent=self.name,
                status="completed",
                summary=f"Retrieved {len(state.evidence)} evidence passages",
                details={"sources": [item.source for item in state.evidence]},
            )
        )
        return state
