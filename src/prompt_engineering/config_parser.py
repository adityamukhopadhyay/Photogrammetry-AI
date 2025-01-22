from pydantic import BaseModel, validator
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
        self.system_prompt = """Convert this 3D modeling prompt into Rodin API JSON configuration:
        - Use 'concat' condition_mode for 2 views
        - Look for PBR values (roughness, metallic)
        - Always set quality=high
        - Identify material types
        - Parse lens optical properties
        - Enable hyper mode
        - Use HighPack addons
        - Output strict JSON with ONLY valid parameters"""
        
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
        
        result = await self.llm.ainvoke(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        try:
            config = json.loads(result.content)
            config["input_image_urls"] = image_urls
            return RodinConfig(**config).model_dump(exclude_none=True)
        except Exception as e:
            raise ValueError(f"Invalid config generation: {str(e)}")