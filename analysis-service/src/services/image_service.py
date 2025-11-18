import os
import logging
import uuid
from typing import Optional

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from google.cloud import storage

logger = logging.getLogger(__name__)

# --- Constants ---
IMAGE_GCS_BUCKET_NAME = os.getenv("GCS_IMAGE_BUCKET", "houseiq-generated-images")
IMAGE_MODEL_NAME = "imagegeneration@006" # The latest model for image generation

from src.services.secret_service import secret_service # Import the new secret service

# ... (other imports)

class ImageGenerationService:
    """
    Purpose: A service to handle image generation using Vertex AI's Imagen model.
             It generates an image from a prompt, uploads it to a GCS bucket,
             and returns a public URL.
    """

    def __init__(self):
        """
        Purpose: Initializes the Vertex AI client and GCS client.
                 Demonstrates fetching a hypothetical API key from Secret Manager.
        """
        try:
            # Attempt to fetch API key from Secret Manager
            api_key = secret_service.get_secret("IMAGEN_API_KEY")
            if api_key:
                logger.info("✓ Hypothetical IMAGEN_API_KEY fetched from Secret Manager.")
            else:
                logger.warning("⚠ Could not fetch IMAGEN_API_KEY from Secret Manager, relying solely on ADC.")

            self.project_id = os.getenv("PROJECT_ID", "houseiq-yourinteriordeco-ai")
            self.location = os.getenv("VERTEX_LOCATION", "us-central1")
            
            vertexai.init(project=self.project_id, location=self.location)
            
            self.model = GenerativeModel(IMAGE_MODEL_NAME)
            self.storage_client = storage.Client()
            
            self.enabled = True
            logger.info(f"✓ Vertex AI ImageGenerationService initialized successfully (project={self.project_id}, location={self.location}, model={IMAGE_MODEL_NAME})")
        except Exception as e:
            self.enabled = False
            self.model = None
            self.storage_client = None
            logger.error(f"✗ Failed to initialize ImageGenerationService: {e}")
            logger.warning("⚠ Image generation will be disabled.")
    # ... (rest of the class)

    def _upload_to_gcs(self, image_bytes: bytes, project_id: str, prompt: str) -> Optional[str]:
        """
        Purpose: Uploads image bytes to GCS and returns a public URL.
        Input:
            image_bytes (bytes): The generated image data.
            project_id (str): The project ID to use as a folder in GCS.
            prompt (str): The original prompt, used for filename generation.
        Output:
            Optional[str]: The public URL of the uploaded image, or None if upload fails.
        """
        if not self.storage_client:
            logger.error("GCS client not initialized. Cannot upload image.")
            return None
        
        try:
            bucket = self.storage_client.bucket(IMAGE_GCS_BUCKET_NAME)
            
            # Create a unique filename
            safe_prompt = "".join(c for c in prompt if c.isalnum() or c in " _-").rstrip()[:50]
            filename = f"{project_id}/{uuid.uuid4()}_{safe_prompt}.png"
            
            blob = bucket.blob(filename)
            blob.upload_from_string(image_bytes, content_type="image/png")
            
            # Make the blob publicly accessible
            blob.make_public()
            
            logger.info(f"Successfully uploaded image to {blob.public_url}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload image to GCS: {e}")
            # Attempt to create the bucket if it doesn't exist
            if "NotFound" in str(e):
                try:
                    logger.info(f"Bucket {IMAGE_GCS_BUCKET_NAME} not found. Attempting to create it...")
                    self.storage_client.create_bucket(IMAGE_GCS_BUCKET_NAME, location=self.location)
                    logger.info(f"Bucket {IMAGE_GCS_BUCKET_NAME} created successfully. Please re-run the generation.")
                except Exception as bucket_e:
                    logger.error(f"Failed to create GCS bucket {IMAGE_GCS_BUCKET_NAME}: {bucket_e}")
            return None

    async def generate_image(
        self,
        prompt: str,
        project_id: str,
        negative_prompt: str = "text, watermark, blurry, low-resolution, ugly, deformed",
        aspect_ratio: str = "1:1"
    ) -> Optional[str]:
        """
        Purpose: Generates an image based on a text prompt and uploads it.
        Input:
            prompt (str): The descriptive prompt for the image.
            project_id (str): The current project ID.
            negative_prompt (str, optional): Items to exclude from the image.
            aspect_ratio (str, optional): The desired aspect ratio ('1:1', '16:9', '9:16').
        Output:
            Optional[str]: The public URL of the generated image, or None if failed.
        """
        if not self.enabled:
            logger.warning("Image generation is disabled. Returning placeholder.")
            return f"https://placehold.co/512x512/EBF0F4/7C8490?text=Image+Generation+Disabled"

        logger.info(f"Generating image for prompt: '{prompt[:100]}...'")
        try:
            response = await self.model.generate_content_async(
                [prompt],
                generation_config={
                    "number_of_images": 1,
                    "negative_prompt": negative_prompt,
                    "aspect_ratio": aspect_ratio,
                }
            )
            
            if response.images:
                image_bytes = response.images[0]._image_bytes
                return self._upload_to_gcs(image_bytes, project_id, prompt)
            else:
                logger.warning("Image generation returned no images.")
                return None
        except Exception as e:
            logger.error(f"Error during image generation: {e}")
            return None

# Singleton instance
image_service = ImageGenerationService()
