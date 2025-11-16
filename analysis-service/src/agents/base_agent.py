from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the system.
    It defines the common interface for agent execution.
    """

    def __init__(self, **kwargs):
        """
        Initializes the agent. Can be used to set up connections 
        to language models, databases, etc.
        """
        pass

    @abstractmethod
    async def run(self, input_data: Any, **kwargs) -> Any:
        """
        The main execution method for the agent.
        
        This method should contain the core logic of the agent. It takes
        some input data, processes it, and returns the result.
        
        :param input_data: The primary data for the agent to process.
        :param kwargs: Additional keyword arguments for context.
        :return: The result of the agent's processing.
        """
        pass

    def get_name(self) -> str:
        """
        Returns the name of the agent.
        """
        return self.__class__.__name__
