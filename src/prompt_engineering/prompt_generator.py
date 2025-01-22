from pathlib import Path
import base64
from src.llm.deepseek_client import DeepSeekClient
from src.utils.logger import configure_logger

logger = configure_logger()

class PromptGenerator:
    def __init__(self):
        self.llm = DeepSeekClient()
        self.template = """Generate a detailed 3D modeling prompt for glasses with these specifications:
        Material: {material}
        Lens Type: {lens_type}
        Measurements: {measurements}
        Branding: {branding}
        Features: {features}
        
        Include these details:
        - Material textures and surface properties
        - Lens optical characteristics (transparency, refractive index, tint)
        - Precise dimensional accuracy (±0.5mm tolerance)
        - Surface engravings and logos (exact positioning)
        - Mechanical components (hinge type, screw details)
        - Any surface imperfections or wear patterns"""

    async def generate(self, specs, image_paths):
        try:
            # Encode images for DeepSeek Vision API
            encoded_images = await self._encode_images(image_paths)
            
            # Generate base prompt from product specs
            base_prompt = self.template.format(
                material=specs.material,
                lens_type=specs.lens_type,
                measurements=specs.measurements,
                branding=", ".join(specs.branding),
                features=", ".join(specs.features)
            )
            
            # Vision analysis prompt
            vision_instructions = """Analyze these eyewear images and extract:
            - Frame material texture details
            - Lens tint/color gradients
            - Hinge mechanism type
            - Logo placements and engraving styles
            - Any visible surface imperfections
            - Measurements validation
            - Unique design elements"""
            
            # Get vision analysis from DeepSeek
            vision_response = await self.llm.invoke_vision(
                prompt=vision_instructions,
                image_urls=encoded_images
            )
            
            # Combine responses with validation
            final_prompt = await self._validate_prompt(base_prompt, vision_response)
            return final_prompt
            
        except Exception as e:
            logger.error(f"Prompt generation failed: {str(e)}")
            raise

    async def _encode_images(self, image_paths):
        encoded_images = []
        for path in image_paths:
            try:
                with open(path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode("utf-8")
                    mime_type = "image/jpeg" if path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
                    encoded_images.append(f"data:{mime_type};base64,{encoded}")
            except Exception as e:
                logger.error(f"Failed to encode image {path}: {str(e)}")
                raise
        return encoded_images

    async def _validate_prompt(self, base_prompt, vision_analysis):
        validation_prompt = f"""Combine these specifications and visual analysis into a final 3D modeling prompt:
        
        Product Specifications:
        {base_prompt}
        
        Visual Analysis:
        {vision_analysis}
        
        Create a comprehensive prompt that:
        1. Prioritizes measurable physical properties
        2. Specifies material PBR values (roughness, metallic)
        3. Details optical properties for lenses
        4. Includes precise mechanical component descriptions
        5. Maintains brand identity elements
        
        Output ONLY the final prompt with no additional formatting."""
        
        return await self.llm.invoke_text(validation_prompt)