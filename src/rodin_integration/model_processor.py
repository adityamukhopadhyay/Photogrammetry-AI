from .api_handler import RodinAPI
from src.utils.logger import configure_logger
import time

logger = configure_logger()

class ModelProcessor:
    def __init__(self):
        self.api = RodinAPI()
        
    def process_product(self, config):
        try:
            logger.info("Submitting Rodin job")
            handler = self.api.submit_job(config)
            
            while True:
                status = fal_client.status(
                    "fal-ai/hyper3d/rodin",
                    handler.request_id,
                    with_logs=True
                )
                
                if isinstance(status, fal_client.InProgress):
                    for log in status.logs:
                        logger.info(f"Rodin: {log['message']}")
                    time.sleep(15)
                else:
                    break
                    
            return fal_client.result(
                "fal-ai/hyper3d/rodin",
                handler.request_id
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise