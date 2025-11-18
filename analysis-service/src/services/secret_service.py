import os
import logging
from typing import Optional, Dict

try:
    from google.cloud import secretmanager
except ImportError:
    secretmanager = None

logger = logging.getLogger(__name__)

class SecretService:
    """
    Purpose: A service to securely access secrets from Google Secret Manager.
             It includes an in-memory cache to reduce redundant API calls.
    """

    def __init__(self):
        """
        Purpose: Initializes the Secret Manager client and cache.
        """
        self.project_id = os.getenv("PROJECT_ID", "houseiq-yourinteriordeco-ai")
        self._cache: Dict[str, str] = {}
        
        if secretmanager:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
                self.enabled = True
                logger.info(f"✓ SecretManagerServiceClient initialized successfully for project {self.project_id}.")
            except Exception as e:
                self.client = None
                self.enabled = False
                logger.error(f"✗ Failed to initialize SecretManagerServiceClient: {e}")
                logger.warning("⚠ Secret management will be disabled. Falling back to environment variables.")
        else:
            self.client = None
            self.enabled = False
            logger.warning("⚠ google-cloud-secret-manager is not installed. Secret management disabled.")

    def get_secret(self, secret_id: str, version_id: str = "latest") -> Optional[str]:
        """
        Purpose: Retrieves a secret's value from Secret Manager or the cache.
                 If Secret Manager is disabled or fails, it falls back to an environment variable.
        Input:
            secret_id (str): The ID of the secret to retrieve (e.g., "GEMINI_API_KEY").
            version_id (str): The version of the secret (defaults to "latest").
        Output:
            Optional[str]: The secret value, or None if not found.
        """
        # Fallback to environment variable if the service is disabled
        if not self.enabled:
            logger.debug(f"Secret service disabled. Falling back to env var for '{secret_id}'.")
            return os.getenv(secret_id)

        # Check cache first
        cache_key = f"{secret_id}:{version_id}"
        if cache_key in self._cache:
            logger.debug(f"Returning cached secret for '{secret_id}'.")
            return self._cache[cache_key]

        logger.info(f"Fetching secret '{secret_id}' from Secret Manager.")
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")
            
            # Cache the secret
            self._cache[cache_key] = secret_value
            logger.info(f"Successfully fetched and cached secret '{secret_id}'.")
            
            return secret_value
        except Exception as e:
            logger.error(f"Failed to access secret '{secret_id}': {e}")
            logger.warning(f"Falling back to environment variable for '{secret_id}'.")
            return os.getenv(secret_id)

# Singleton instance
secret_service = SecretService()
