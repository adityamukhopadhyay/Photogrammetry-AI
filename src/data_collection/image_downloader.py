import requests
import os
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm

class ImageDownloader:
    def __init__(self, save_dir="data/raw_images"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def download(self, urls):
        downloaded_paths = []
        for url in tqdm(urls, desc="Downloading images"):
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                
                filename = os.path.basename(urlparse(url).path)
                save_path = self.save_dir / filename
                
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_paths.append(str(save_path))
            except Exception as e:
                print(f"Failed to download {url}: {str(e)}")
        
        return downloaded_paths