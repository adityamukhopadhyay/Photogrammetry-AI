import logging
import fal_client
import os
from typing import Dict, Any
import requests
import json
from pathlib import Path

class RodinAPI:
    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")
        logging.debug("Loading FAL_KEY from environment")
        if not self.api_key:
            logging.debug("FAL_KEY not found in environment")
            raise ValueError("FAL_KEY environment variable is not set")
        logging.debug("FAL_KEY successfully loaded")
        
    def _extract_value(self, text: str, parameter: str) -> float:
        """Extract parameter value from text, supporting both key=value and key: value formats.
        
        Args:
            text: The text to search in
            parameter: Parameter name to find (e.g., 'roughness', 'metallic')
        
        Returns:
            float: Extracted value or 0.0 if not found
        """
        import re
        
        # Try both patterns
        patterns = [
            f"{parameter}=([0-9.]+)",  # matches parameter=0.4
            f"{parameter}:\\s*([0-9.]+)",  # matches parameter: 0.4 or PBR parameter: 0.4
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return 0.0
        
    def submit_job(self, config: Dict[str, Any]):
        required = ["prompt", "input_image_urls"]
        if "roughness" in config["prompt"]:
            config["material_parameters"] = {
                "roughness": self._extract_value(config["prompt"], "roughness"),
                "metallic": self._extract_value(config["prompt"], "metallic")
            }
        if not all(k in config for k in required):
            raise ValueError("Missing required config parameters")
            
        return fal_client.subscribe(
            "fal-ai/hyper3d/rodin",
            arguments=config,
            with_logs=True
        )
    
    def save_result(self, result, product_id):
        logging.info(f"Starting to save result for product {product_id}")
        
        # Validate result structure
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict result, got {type(result)}")
        if "model_mesh" not in result or "url" not in result["model_mesh"]:
            raise ValueError("Invalid result structure: missing model_mesh or url")
        if "textures" not in result:
            raise ValueError("Invalid result structure: missing textures")
            
        output_dir = Path("data/3d_models") / product_id
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created output directory: {output_dir}")
        
        model_path = output_dir / "model.glb"
        textures_dir = output_dir / "textures"
        textures_dir.mkdir(exist_ok=True)
        
        # Download main model
        logging.info(f"Downloading GLB model from {result['model_mesh']['url']}")
        try:
            response = requests.get(result["model_mesh"]["url"])
            response.raise_for_status()
            
            # Verify content type
            content_type = response.headers.get('content-type', '')
            if 'model/gltf-binary' not in content_type and 'application/octet-stream' not in content_type:
                logging.warning(f"Unexpected content type for GLB: {content_type}")
                
            with open(model_path, "wb") as f:
                f.write(response.content)
            logging.info(f"Successfully saved GLB model to {model_path}")
        except requests.RequestException as e:
            logging.error(f"Failed to download GLB model: {str(e)}")
            raise
            
        # Download textures
        for i, texture in enumerate(result["textures"]):
            if "url" not in texture:
                logging.error(f"Invalid texture structure at index {i}")
                continue
                
            tex_path = textures_dir / f"texture_{i}.png"
            logging.info(f"Downloading texture {i} from {texture['url']}")
            try:
                response = requests.get(texture["url"])
                response.raise_for_status()
                
                # Verify content type
                content_type = response.headers.get('content-type', '')
                if 'image' not in content_type:
                    logging.warning(f"Unexpected content type for texture: {content_type}")
                    
                with open(tex_path, "wb") as f:
                    f.write(response.content)
                logging.info(f"Successfully saved texture to {tex_path}")
            except requests.RequestException as e:
                logging.error(f"Failed to download texture {i}: {str(e)}")
                # Continue with other textures even if one fails
                
        logging.info(f"Completed saving result for product {product_id}")
        return str(output_dir)
