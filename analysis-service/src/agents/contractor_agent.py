from src.agents.base_agent import BaseAgent
from src.models.project import ProjectBrief, Quote
from src.services.llm_service import mock_llm_service
import logging

logger = logging.getLogger(__name__)

class ContractorAgent(BaseAgent):
    """
    The Contractor Agent is responsible for generating a detailed,
    structured quote based on the project brief.
    """

    async def run(self, brief: ProjectBrief, **kwargs) -> Quote:
        """
        Takes a project brief and generates a detailed quote.
        
        :param brief: The ProjectBrief object created by the Client Manager.
        :return: A structured Quote object.
        """
        logger.info(f"ContractorAgent activated for project {brief.project_id}.")

        # 1. Construct a prompt for the LLM to generate a quote
        prompt = (
            "You are a professional and experienced contractor. "
            "Based on the following project brief, generate a detailed and "
            "structured quote. Include missing items that are critical for safety "
            "and longevity, and mark them as suggestions.\n\n"
            f"--- PROJECT BRIEF ---\n"
            f"House Type: {brief.user_profile.get('house_type')}\n"
            f"Budget: {brief.user_profile.get('budget')}\n"
            f"Key Requirements: {', '.join(brief.key_requirements)}\n"
            f"Style: {', '.join(brief.style_preferences)}\n"
            f"--- END BRIEF ---\n\n"
            "Please generate a structured quote in JSON format."
        )

        # 2. Call the (mock) LLM service to get structured data
        quote_data = await mock_llm_service.generate_response(
            prompt=prompt,
            context={"project_id": brief.project_id, "task": "generate_quote"}
        )

        # 3. Create and return the Pydantic model
        generated_quote = Quote(**quote_data)
        
        logger.info(f"Successfully generated quote for project {brief.project_id}.")
        return generated_quote
