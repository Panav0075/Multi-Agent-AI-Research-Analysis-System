from copy import deepcopy


class WorkflowMemory:
    """Small in-process checkpoint store for workflow state."""

    def __init__(self):
        self._checkpoints = []

    def save(self, state):
        self._checkpoints.append(deepcopy(state))

    def latest(self):
        if not self._checkpoints:
            return None
        return deepcopy(self._checkpoints[-1])

    def history(self):
        return deepcopy(self._checkpoints)

    def __len__(self):
        return len(self._checkpoints)
