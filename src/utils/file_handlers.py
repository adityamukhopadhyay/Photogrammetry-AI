from pathlib import Path
import json

class FileManager:
    @staticmethod
    def save_prompt(prompt_text, product_id):
        prompt_dir = Path("data/prompts")
        prompt_dir.mkdir(exist_ok=True)
        path = prompt_dir / f"{product_id}_prompt.txt"
        path.write_text(prompt_text)
        return path
    
    @staticmethod
    def save_config(config, product_id):
        config_dir = Path("data/configs")
        config_dir.mkdir(exist_ok=True)
        path = config_dir / f"{product_id}_config.json"
        path.write_text(json.dumps(config, indent=2))
        return path