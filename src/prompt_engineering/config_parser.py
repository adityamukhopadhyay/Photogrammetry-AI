from pydantic import BaseModel
from enum import Enum
import json
from typing import Optional

class ConditionMode(str, Enum):
    fuse = "fuse"
    concat = "concat"

class RodinConfig(BaseModel):
    prompt: str
    input_image_urls: list[str]
    condition_mode: ConditionMode = ConditionMode.concat
    geometry_file_format: str = "glb"
    material: str = "PBR"
    quality: str = "high"
    tier: str = "Regular"
    use_hyper: bool = True
    addons: Optional[str] = "HighPack"
    seed: Optional[int] = None
    bbox_condition: Optional[list[int]] = None

class ConfigGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = '''Return a valid JSON configuration for the Rodin API. Your response must be ONLY a JSON object.

        Example format:
        {
            "prompt": "create a detailed 3D model...",
            "condition_mode": "concat",
            "material": "PBR",
            "quality": "high",
            "addons": "HighPack",
            "geometry_file_format": "glb",
            "tier": "Regular",
            "use_hyper": true
        }

        Requirements:
        - Use 'concat' condition_mode for 2 views
        - Look for PBR values (roughness, metallic)
        - Always set quality=high
        - Identify material types
        - Parse lens optical properties
        - Enable hyper mode
        - Use HighPack addons
        - Output ONLY the JSON object, no additional text'''
        
    async def generate_config(self, prompt_text, image_urls):
        user_prompt = f"""Prompt:
        {prompt_text}
        
        Image URLs: {image_urls}
        
        Generate configuration with these rules:
        - condition_mode: concat
        - material: PBR
        - quality: high
        - addons: HighPack
        - geometry_file_format: glb
        - tier: Regular
        - use_hyper: true"""
        
        combined_prompt = f"{self.system_prompt}\n\n{user_prompt}"
        
        result = await self.llm.ainvoke(combined_prompt)

        try:
            # Clean up common JSON formatting issues
            result = result.strip()
            # Remove any markdown code block markers
            result = result.replace("```json", "").replace("```", "")
            # Find the first '{' and last '}' to extract just the JSON object
            start = result.find('{')
            end = result.rfind('}') + 1
            if start >= 0 and end > 0:
                result = result[start:end]
            
            # Parse the cleaned JSON
            config = json.loads(result)
            
            # Validate required fields
            if not isinstance(config, dict):
                raise ValueError("Response is not a JSON object")
            if "prompt" not in config:
                raise ValueError("Missing required 'prompt' field")
                
            config["input_image_urls"] = image_urls
            return RodinConfig(**config).model_dump(exclude_none=True)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}, Response: {result}")
        except Exception as e:
            raise ValueError(f"Config generation failed: {str(e)}, Response: {result}")
