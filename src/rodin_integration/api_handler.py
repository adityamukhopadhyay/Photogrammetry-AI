import fal_client
import os
from typing import Dict, Any
import json
from pathlib import Path

class RodinAPI:
    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")
        
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
        output_dir = Path("data/3d_models") / product_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = output_dir / "model.glb"
        textures_dir = output_dir / "textures"
        textures_dir.mkdir(exist_ok=True)
        
        # Download main model
        with open(model_path, "wb") as f:
            f.write(requests.get(result["model_mesh"]["url"]).content)
            
        # Download textures
        for i, texture in enumerate(result["textures"]):
            tex_path = textures_dir / f"texture_{i}.png"
            with open(tex_path, "wb") as f:
                f.write(requests.get(texture["url"]).content)
                
        return str(output_dir)