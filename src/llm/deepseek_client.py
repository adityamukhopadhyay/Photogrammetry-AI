from openai import AsyncOpenAI
import os
from src.utils.logger import configure_logger
import base64
import logging
from pathlib import Path

class DeepSeekClient:
    def __init__(self):
        self.logger = configure_logger()
        self.client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.logger.info("DeepSeek client initialized with API key")
        
    async def ainvoke(self, prompt: str, images: list = None, model: str = "deepseek-reasoner"):
        """Process text and/or images with detailed logging"""
        try:
            self.logger.debug("Starting API request preparation")
            messages = [{"role": "user", "content": prompt}]
            operation_type = "text-only"

            self.logger.info(f"Sending {operation_type} request to model {model}")
            self.logger.debug(f"Request payload preview:\n{messages[0]['content'][:200]}...")

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=4000
            )

            self.logger.success(f"API request completed successfully")
            self.logger.debug(
                f"Response metadata: "
                f"Tokens used - {response.usage.total_tokens} "
                f"(Prompt: {response.usage.prompt_tokens}, "
                f"Completion: {response.usage.completion_tokens})"
            )
            
            response_content = response.choices[0].message.content
            self.logger.debug(f"Response content preview:\n{response_content[:200]}...")
            
            return response_content
            
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            self.logger.debug(f"Error details: {vars(e)}")
            raise

    async def _encode_image(self, image_path):
        """Encode image with size logging and error handling"""
        try:
            self.logger.debug(f"Processing image: {image_path}")
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                encoded = base64.b64encode(image_data).decode("utf-8")
                
                # Determine MIME type and log details
                file_ext = Path(image_path).suffix.lower()
                mime = "image/jpeg" if file_ext in (".jpg", ".jpeg") else "image/png"
                self.logger.debug(
                    f"Encoded image: {Path(image_path).name} | "
                    f"Type: {mime} | "
                    f"Size: {len(image_data)//1024} KB"
                )
                
                return f"data:{mime};base64,{encoded}"
                
        except Exception as e:
            self.logger.error(f"Image encoding failed for {image_path}: {str(e)}")
            raise