import logging
from typing import Dict

logger = logging.getLogger(__name__)

class MockImageGenerationService:
    """
    A mock Image Generation service that simulates calls to a real model like Gemini.
    This is used for local development without needing live API keys.
    """

    async def generate_image(self, prompt: str) -> Dict[str, str]:
        """
        Simulates generating an image from a text prompt.

        :param prompt: The text prompt for image generation.
        :return: A dictionary containing the URL of a placeholder image.
        """
        logger.info(f"--- MOCK IMAGE GENERATION SERVICE CALLED ---")
        logger.info(f"Prompt: {prompt[:200]}...")
        logger.info(f"------------------------------------------")

        # Return a URL to a placeholder image.
        # The size (e.g., 800x600) can be adjusted as needed.
        # The text is URL-encoded to be displayed on the placeholder.
        encoded_prompt = prompt.replace(" ", "+")
        image_url = f"https://via.placeholder.com/800x600.png?text={encoded_prompt}"

        return {
            "image_url": image_url,
            "message": "Image generated successfully (mock)."
        }

# Singleton instance
mock_image_generation_service = MockImageGenerationService()
