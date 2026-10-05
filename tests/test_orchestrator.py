from src.orchestrator import MultiAgentOrchestrator


def test_workflow_completes_with_trace():
    system = MultiAgentOrchestrator.from_config("config.yaml")
    state = system.run(
        "Should we prioritize reducing first-response time or improving self-service documentation coverage?"
    )

    agents = [event.agent for event in state.trace]

    assert state.final_answer
    assert "planner" in agents
    assert "researcher" in agents
    assert "analyst" in agents
    assert "critic" in agents
    assert "writer" in agents
    assert state.trace[-1].status == "completed"


def test_final_answer_contains_sources():
    system = MultiAgentOrchestrator.from_config("config.yaml")
    state = system.run(
        "Is there evidence that improving troubleshooting documentation can reduce support workload?"
    )
    assert "Sources" in state.final_answer
    assert "knowledge-base-study.md" in state.final_answer
