from pathlib import Path
import base64
from src.llm.deepseek_client import DeepSeekClient
from src.utils.logger import configure_logger

logger = configure_logger()

class PromptGenerator:
    def __init__(self, llm=None):
        self.llm = llm if llm is not None else DeepSeekClient()
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
                - Include RGB color codes 
                - Specify material PBR values (roughness 0-1 scale)
                - Maintain technical terminology

                very detailed output"""
            
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
        validation_prompt = f"""Combine these technical specifications and visual analysis into a production-ready 3D modeling prompt:  
        
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

        Technical Requirements that must be included if available, based on the {base_prompt} and {vision_analysis}:
        1. Material Properties:
        - Specify PBR values: roughness (0.0-1.0), metallic (0.0-1.0)
        - Detail material layering (acetate core/lamination)
        - Include surface imperfection maps (micro-scratches, tooling marks)

        2. Geometric Requirements:
        - Reference both angled (45°) and front (0°) views for:
        - Bridge curvature radius (±0.2mm tolerance)
        - Temple arm taper gradient
        - Lens bevel angle (edge thickness profile)
        - Maintain inter-pupillary distance alignment between views

        3. Branding Implementation:
        - Etch "WARBY PARKER" text on left temple:
        - Position: 10mm from hinge centerpoint
        - Engraving: 0.3mm depth debossed
        - Font: Sans-serif, 2.5mm height
        - Alignment: Follow temple curvature (3° radial offset)

        4. Optical Requirements:
        - Lens parameters:
        - Base curve: 4-8 diopter range
        - Refractive index: 1.50-1.74
        - ABBE value: ≥30
        - Edge polish: 0.5mm matte bevel

        5. Mechanical Components:
        - Hinge specifications:
        - Barrel count: 3-5 components
        - Spring tension: 500-700gf
        - Screw type: M1.4×3mm flathead
        - Nose pad material: Medical-grade silicone (Shore 50A)

        6. Quality Assurance:
        - Prevent these artifacts:
        - Texture UV stretching
        - Color value mismatches (ΔE < 2.0)
        - Edge detailing errors (maintain 0.1mm feature resolution)
        - Surface normal inconsistencies between views

        !!All the above points should be based on the provided Product specifications and visual analysis ONLY!!
        
        !!Output ONLY the final 3D prompt with no additional formatting.!!
        !!It should also have lines like Create a 3D model of a pair of glasses based on the given specifications and visual analysis of the glasses.({base_prompt} and {vision_analysis})!!
        
        example prompt that works: 
        'Create a 3D model of brown tortoise-shell eyeglasses with a frame made of polished cellulose acetate. Ensure the frame exhibits a marbled pattern with varying shades of brown, maintaining a glossy finish (PBR roughness: 0.1-0.2, metallic: 0).
        Include "Warby Parker" branding etched onto the left temple, positioned precisely 10mm from the hinge, with debossed engraving details.
        Model the lens as clear polycarbonate with anti-reflective and scratch-resistant coatings, ensuring full UV protection. Set transparency and reflectivity to represent these optical properties accurately.
        Set the frame width measurements to 134mm for medium and 138mm for wide.
        Incorporate small metallic rivets on the temples with a polished finish (PBR metallic: 0.8, roughness: 0.1).
        Add standard metal hinges for the temple arms, ensuring mechanical accuracy and alignment with the frame material.
        Model the nose pads as part of the acetate frame design without additional adjustability.
        Ensure the lens refractive index is set to 1.586 to match standard polycarbonate material properties.
        Reflect the smooth, glossy surface of the acetate frame throughout the model, ensuring consistency across temple arms and the brow bar.
        Maintain the oversized lens design and signature graduated rivet details, emphasizing their placement and alignment for brand identity preservation.'

        !!!!Important Note: If there's no mentioned tint on the glasess lens, then the tint should be clear, transparent and the color intensity should be 0.0
        Prompt should also majorly focus on the uploaded images to determine how it should look
        Glass lenses will almost always be fully transparent or might have a very subtle tint but lens will be transparent(use 3D terminologies to ensure transparency of lens)!!!!!!

        Finally, the prompt shouldn't be too complex to understand by the AI model. It should be simple and easy to understand with all visual details and product specifications.
        !!And maximum focus is on the INPUT IMAGES to determine the final output of the 3D model.!!
        and if glass lens is transparent, then the color intensity should be 0.0(example prompt could be: 'Model the lens as clear polycarbonate with anti-reflective and scratch-resistant coatings, ensuring full UV protection. Set transparency and reflectivity to represent these optical properties accurately.' )
        make sure i dont get opaque lens in the 3D model whatsover, it should be transparent and clear lens.
        !!keywords: ULTRA-PRECISE 3D EYEWEAR MODEL - CRYSTAL CLEAR LENSES REQUIRED.!!
        lines like these 'Use polycarbonate lenses (refractive index: 1.49) with crystal-clear transparency (0.0 color intensity)
        MANDATORY USE WORDS: like "crystal-clear transparency" when lens is transparent 
'"""
        
        return await self.llm.ainvoke(validation_prompt)