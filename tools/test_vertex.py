import os
import json
from google import genai
from google.genai import types

project_id = os.getenv("PROJECT_ID", "nooko-yourinteriordeco-ai")
location = os.getenv("VERTEX_LOCATION", "us-central1")
model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-002")
preferred_backend = os.getenv("GEMINI_BACKEND", "auto").lower()
api_key = os.getenv("GEMINI_API_KEY")

client = None
if preferred_backend == "api" or (preferred_backend == "auto" and api_key):
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required when GEMINI_BACKEND=api.")
    client = genai.Client(api_key=api_key)
else:
    client = genai.Client(vertexai=True, project=project_id, location=location)

content = [
    types.Content(role="user", parts=[types.Part.from_text(text="Hi, summarize yourself in one sentence.")])
]

response = client.models.generate_content(model=model_name, contents=content)
print(json.dumps({"text": response.text}, ensure_ascii=False))
