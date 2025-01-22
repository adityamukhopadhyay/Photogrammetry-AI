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
            vision_instructions = """Analyze these eyewear images and extract these specific details(if present):
            1. Frame Material Analysis:
            - Identify material type (acetate, titanium, stainless steel, etc.)
            - Note surface texture details: 
            • Marbling patterns (vein density/color distribution)
            • Layered acetate composition (visible layer count)
            • Surface finish (matte, glossy, brushed metal)
            - Document material thickness variations (temple vs front)

            2. Logo & Branding Elements:
            - Locate exact placement of "WARBY PARKER" text:
            • Side (left/right temple)
            • Position from hinge (e.g., 25mm from hinge on left temple)
            • Engraving depth and style (embossed/debossed/printed)

            3. Lens Specifications:
            - Tint gradient analysis:
            • Gradient direction (top-bottom/left-right)
            • Color intensity mapping (RGB values estimation)
            • Transition sharpness (gradual/abrupt)
            - Surface properties:
            • Reflectivity (mirror/anti-reflective coating)
            • Presence of polarization patterns
            • Edge bevel details (polished/rough)

            4. Hinge Mechanism Documentation:
            - Hinge type identification:
            • Barrel hinge (number of barrels)
            • Spring hinge (visible coil mechanism)
            • Screwless magnetic closure
            - Component materials (stainless steel, nickel alloy)
            - Screw characteristics:
            • Head type (phillips/flat/hex)
            • Count per hinge
            • Symmetry between sides

            5. Measurement Validation:
            - Verify advertised measurements using visual references:
            • Bridge width (distance between lenses)
            • Temple length (from hinge to tip)
            • Lens height/width ratio
            - Identify physical measurement markers:

            6. Unique Design Features:
            - Architectural elements:
            • Decorative rivets (material/count)
            • Temple end designs (curved/flat)
            • Nose pad materials (silicone/acetate)
            - Functional components:
            • Adjustable nose pads
            • Cable temple tips
            • Hidden spring mechanisms

            Format Requirements:
            - Use precise millimeter measurements
            - Note left/right orientation
            - Include RGB color codes where applicable
            - Specify material PBR values (roughness 0-1 scale)
            - Maintain technical terminology"""
            
            # Get vision analysis from DeepSeek
            vision_response = await self.llm.ainvoke(
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
        
        return await self.llm.ainvoke(validation_prompt)