from .api_handler import RodinAPI
from src.utils.logger import configure_logger
import time
import fal_client
import requests

logger = configure_logger()

class ModelProcessor:
    def __init__(self):
        self.api = RodinAPI()

    def process_product(self, config):
        try:
            logger.info("Submitting Rodin job")
            handler = self.api.submit_job(config)
            
            logger.debug(f"Received handler object: {handler}")
            logger.debug(f"Handler type: {type(handler)}")
            
            # while True:
            #     status = handler.status(with_logs=True)
                
            #     if isinstance(status, fal_client.InProgress):
            #         for log in status.logs:
            #             logger.info(f"Rodin: {log['message']}")
            #         time.sleep(15)
            #     else:
            #         break
                    
            result = handler['model_mesh']['url']
            
            logger.info("Received result from Rodin API")
            logger.debug(f"Result structure: {result}")
            
            try:
                output_path = self.api.save_result(result, config.get('product_id'))
                logger.info(f"Successfully saved model files to {output_path}")
                return result
            except ValueError as ve:
                logger.error(f"Invalid result structure: {str(ve)}")
                raise
            except requests.RequestException as re:
                logger.error(f"Failed to download model files: {str(re)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error while saving result: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            # Download the model using the link
            try:
                logger.info("Attempting to download the model directly")
                print("Attempting to download the model directly")
                response = requests.get(result)
                response.raise_for_status()
                
                # Save the model to a file
                model_path = "data/3d_models/model.glb"
                with open(model_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Successfully downloaded and saved model to {model_path}")
                print(f"Successfully downloaded and saved model to {model_path}")
                
                return model_path
            
            except requests.RequestException as e:
                logger.error(f"Failed to download model: {str(e)}")
                print(f"Failed to download model: {str(e)}")
                raise