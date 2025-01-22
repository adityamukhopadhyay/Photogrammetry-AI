import os
import httpx
from typing import List, Dict
from pydantic import BaseModel
from src.utils.logger import configure_logger

logger = configure_logger()

class DeepSeekMessage(BaseModel):
    role: str  # "system" or "user"
    content: str
    images: List[str] = []

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_URL")
        self.timeout = 30
        self.max_retries = 3

    async def _make_request(self, messages: List[Dict], model: str = "deepseek-chat") -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "top_p": 0.3,
            "max_tokens": 4000
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=headers
                    )
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
                    
                except httpx.HTTPStatusError as e:
                    logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    raise

    async def invoke_vision(self, prompt: str, image_urls: List[str]) -> str:
        messages = [{
            "role": "user",
            "content": prompt,
            "images": image_urls
        }]
        return await self._make_request(messages, "deepseek-vision")

    async def invoke_text(self, prompt: str) -> str:
        messages = [{
            "role": "user",
            "content": prompt
        }]
        return await self._make_request(messages)