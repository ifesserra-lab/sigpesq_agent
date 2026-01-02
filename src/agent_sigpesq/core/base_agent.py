from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')
R = TypeVar('R')

class BaseAgent(ABC, Generic[T, R]):
    """
    Abstract base class for agents following SOLID principles.
    Uses Generics for input (T) and output (R).
    """

    @abstractmethod
    async def run(self, input_data: T) -> R:
        """
        Executes the agent's logic.
        """
        pass
