import yaml

from .agents.analyst import AnalysisAgent
from .agents.critic import CriticAgent
from .agents.planner import PlannerAgent
from .agents.researcher import ResearchAgent
from .agents.writer import WriterAgent
from .memory import WorkflowMemory
from .schemas import TraceEvent, WorkflowState
from .tools.knowledge_search import KnowledgeSearchTool


class MultiAgentOrchestrator:
    def __init__(
        self,
        planner,
        researcher,
        analyst,
        critic,
        writer,
        max_retries=1,
    ):
        self.planner = planner
        self.researcher = researcher
        self.analyst = analyst
        self.critic = critic
        self.writer = writer
        self.max_retries = max_retries

    @classmethod
    def from_config(cls, config_path="config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        search_tool = KnowledgeSearchTool(cfg["knowledge"]["path"])

        return cls(
            planner=PlannerAgent(),
            researcher=ResearchAgent(
                search_tool,
                top_k=cfg["knowledge"]["top_k"],
            ),
            analyst=AnalysisAgent(),
            critic=CriticAgent(),
            writer=WriterAgent(),
            max_retries=cfg["workflow"]["max_retries"],
        )

    def run(self, request):
        state = WorkflowState(request=request)
        memory = WorkflowMemory()

        state.trace.append(
            TraceEvent(
                agent="orchestrator",
                status="started",
                summary="Started multi-agent workflow",
            )
        )

        state = self.planner.run(state)
        memory.save(state)

        while True:
            state = self.researcher.run(state)
            memory.save(state)

            state = self.analyst.run(state)
            memory.save(state)

            state = self.critic.run(state)
            memory.save(state)

            if state.critique.get("approved"):
                break

            if state.retry_count >= self.max_retries:
                state.trace.append(
                    TraceEvent(
                        agent="orchestrator",
                        status="retry_limit_reached",
                        summary="Stopped revision loop at configured retry limit",
                    )
                )
                break

            state.retry_count += 1
            state.trace.append(
                TraceEvent(
                    agent="orchestrator",
                    status="retrying",
                    summary=f"Starting revision pass {state.retry_count}",
                )
            )

        state = self.writer.run(state)

        state.trace.append(
            TraceEvent(
                agent="orchestrator",
                status="completed",
                summary="Workflow completed",
                details={"checkpoints": len(memory)},
            )
        )
        return state
