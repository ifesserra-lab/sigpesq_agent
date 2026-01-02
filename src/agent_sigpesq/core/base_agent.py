"""
Module for the base agent.

This module defines the abstract base class for all agents in the system,
enforcing a standard interface and type safety.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')
R = TypeVar('R')

class BaseAgent(ABC, Generic[T, R]):
    """
    Abstract base class for agents following SOLID principles.
    
    This class defines a generic contract for agents, where T is the input type
    and R is the return type of the run method.

    Type Parameters:
        T: The type of input data the agent accepts.
        R: The type of result the agent returns.
    """

    @abstractmethod
    async def run(self, input_data: T) -> R:
        """
        Executes the agent's main logic.

        Args:
            input_data (T): The input data required for the agent's operation.

        Returns:
            R: The result of the agent's execution.
        """
        pass
