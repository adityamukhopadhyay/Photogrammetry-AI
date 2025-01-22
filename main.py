import asyncio  
from dotenv import load_dotenv
from src.data_collection.image_downloader import ImageDownloader
from src.data_collection.product_scraper import WarbyScraper
from src.image_processing.image_enhancer import ImageEnhancer
from src.prompt_engineering.prompt_generator import PromptGenerator
from src.prompt_engineering.config_parser import ConfigGenerator
from src.rodin_integration.api_handler import RodinAPI
from src.utils.file_handlers import FileManager
from src.llm.deepseek_client import DeepSeekClient
from src.utils.logger import configure_logger

# Initialize logging
logger = configure_logger()
logger.info("Application started")

async def main(product_url):
    load_dotenv()
    
    # Initialize DeepSeek client
    llm_client = DeepSeekClient()
    
    # Initialize components
    downloader = ImageDownloader()
    enhancer = ImageEnhancer()
    
    # Scrape product data
    scraper = WarbyScraper(llm=llm_client)
    specs = await scraper.scrape(product_url)
    
    # Download and process images
    image_paths = downloader.download([product_url + "/images"])
    enhanced_paths = [enhancer.enhance(p) for p in image_paths]
    
    # Generate prompt
    prompt_gen = PromptGenerator(llm=llm_client)
    prompt_text = await prompt_gen.generate(specs, enhanced_paths)
    FileManager.save_prompt(prompt_text, specs.product_id)
    
    # Generate Rodin config
    config_gen = ConfigGenerator(llm=llm_client)
    config = await config_gen.generate_config(prompt_text, enhanced_paths)
    FileManager.save_config(config, specs.product_id)
    
    # Submit to Rodin
    rodin = RodinAPI()
    result = rodin.submit_job(config)
    output_dir = rodin.save_result(result, specs.product_id)
    
    print(f"3D model generated at: {output_dir}")

if __name__ == "__main__":
    product_url = input("Enter Warby Parker product URL: ")
    asyncio.run(main(product_url))