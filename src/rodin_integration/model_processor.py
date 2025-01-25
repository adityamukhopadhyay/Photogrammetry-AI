from .api_handler import RodinAPI
from src.utils.logger import configure_logger
import requests

logger = configure_logger()

class ModelProcessor:
    def __init__(self):
        self.api = RodinAPI()

    def process_product(self, config):
        """
        Process a product using Rodin API and download the resulting 3D model.
        
        Args:
            config: Configuration dictionary for the job
            
        Returns:
            str: Path to the downloaded model file
            
        Raises:
            requests.RequestException: If model download fails
        """
        try:
            print("\n🚀 Starting 3D job submission...")
            logger.info("Submitting Rodin job")
            handler = self.api.submit_job(config)
            logger.debug(f"Received handler object: {handler}")
            print("\n✅ Job submitted successfully")
            
            result = handler['model_mesh']['url']
            logger.info("Received result from Rodin API")
            logger.debug(f"Result structure: {result}")
            print(f"\n📥 Received model URL from Rodin API: {result}")

            print("\n⏳ Downloading model file...")
            logger.info("Attempting to download the model")
            response = requests.get(result)
            response.raise_for_status()
            
            model_path = "data/3d_models/model.glb"
            with open(model_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Successfully downloaded and saved model to {model_path}")
            print(f"\n✅ Model successfully downloaded to: {model_path}")
            
            return model_path
            
        except requests.RequestException as e:
            error_msg = f"❌ Download failed: {str(e)}"
            print(error_msg)
            logger.error(f"Failed to download model: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"❌ Processing failed: {str(e)}"
            print(error_msg)
            logger.error(f"Processing failed: {str(e)}")
            raise
