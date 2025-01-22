import cv2
import numpy as np
from pathlib import Path

class ImageEnhancer:
    def __init__(self, output_dir="data/processed_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def enhance(self, image_path):
        img = cv2.imread(str(image_path))
        
        # Contrast enhancement
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        limg = cv2.merge([clahe.apply(l), a, b])
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # Save processed image
        output_path = self.output_dir / f"enhanced_{image_path.name}"
        cv2.imwrite(str(output_path), enhanced)
        return output_path