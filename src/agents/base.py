from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name = "base"

    @abstractmethod
    def run(self, state):
        raise NotImplementedError
