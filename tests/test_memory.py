from src.memory import WorkflowMemory
from src.schemas import WorkflowState


def test_memory_saves_independent_checkpoint():
    memory = WorkflowMemory()
    state = WorkflowState(request="test")
    memory.save(state)

    state.request = "changed"

    assert memory.latest().request == "test"
    assert len(memory) == 1
