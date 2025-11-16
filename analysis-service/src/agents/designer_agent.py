from src.agents.base_agent import BaseAgent
from src.models.project import ProjectBrief
from src.services.image_generation_service import mock_image_generation_service
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class DesignerAgent(BaseAgent):
    """
    The Designer Agent is responsible for generating a final concept rendering
    based on the project brief.
    """

    async def run(self, brief: ProjectBrief, **kwargs) -> Dict[str, str]:
        """
        Takes a project brief and generates a concept rendering.
        
        :param brief: The ProjectBrief object created by the Client Manager.
        :return: A dictionary containing the URL of the generated image.
        """
        logger.info(f"DesignerAgent activated for project {brief.project_id}.")

        # 1. Construct a detailed prompt for the final rendering
        style = ", ".join(brief.style_preferences)
        requirements = ", ".join(brief.key_requirements)
        
        prompt = (
            "A high-quality, photorealistic final concept rendering of an interior space. "
            f"The style is {style}. "
            f"Key features to include are: {requirements}. "
            f"The house is a {brief.user_profile.get('house_type', 'unknown type')}."
        )

        # 2. Call the (mock) image generation service
        image_data = await mock_image_generation_service.generate_image(prompt=prompt)
        
        logger.info(f"Successfully generated final rendering for project {brief.project_id}.")
        
        # 3. Return the result
        return image_data
