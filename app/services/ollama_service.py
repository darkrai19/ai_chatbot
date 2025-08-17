import httpx
from app.core.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL_NAME

    async def generate_sql_query(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                response_data = response.json()
                # Assuming the response format is a simple string.
                # You might need to parse this depending on the actual Ollama response.
                return response_data.get("response", "").strip()
            except httpx.HTTPStatusError as e:
                # Handle HTTP errors from the Ollama server
                raise Exception(f"Ollama server error: {e.response.text}")
            except Exception as e:
                # Handle other exceptions
                raise Exception(f"Failed to communicate with Ollama: {e}")