from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import asyncio
import time
import os
import json
from src.rodin_integration import ModelProcessor
from src.llm.deepseek_client import DeepSeekClient
from src.prompt_engineering import ConfigGenerator
from src.prompt_engineering import PromptGenerator
from src.data_collection.product_scraper import WarbyScraper
# from data_collection.product_scraper import WarbyScraper

if os.path.exists("vision_analysis.txt") and os.path.exists("product_details.txt"):
    with open("vision_analysis.txt", "r") as file:
        vision_analysis = file.read()
    with open("product_details.txt", "r") as file:
        product_details = file.read()
    print(f'\n\nVision Analysis:\n{vision_analysis}\n\nProduct Details:\n{product_details}')

else: 

    # URL of the website
    url = "https://imageprompt.org/describe-image"
    load_dotenv()
    img_url=[]

    # Initialize DeepSeek client
    product_details = None

    async def main():
        global product_details
        llm_client = DeepSeekClient()
        product_url = input("Enter Warby Parker product URL: ")

        scraper = WarbyScraper(llm=llm_client)
        product_details = await scraper.scrape(product_url)
        print("\n\nExtracted Product Details:\n", product_details)

        # Save product details to a text file
        with open("product_details.txt", "w") as file:
            file.write(str(product_details))

        print("\n\nExtracted Image URLs:")
        print(scraper.image_urls[0]+'\n'+
        scraper.image_urls[1])
        # Save image URLs to a text file
        with open("img_list.txt", "w") as file:
            file.write(scraper.image_urls[0] + '\n' + scraper.image_urls[1])
        print("Saved image URLs to 'img_list.txt'")

        # Your image URL to input
        img_url.append(scraper.image_urls[0])


    # Set up the WebDriver service
    asyncio.run(main())
    vision_instructions = """Analyze these eyewear images and extract these specific details(if present):
                    1. Frame Material Analysis:
                    - Identify material type (acetate, titanium, stainless steel, etc.)
                    - Note surface texture details: 
                    • Marbling patterns (vein density/color distribution)
                    . try to extract precise color codes for the marbling patterns, noting the density and distribution of the veins. Provide detailed information on the color variations and their spatial arrangement.
                    • Layered acetate composition (visible layer count)
                    • Surface finish (matte, glossy, brushed metal)
                    - Document material thickness variations (temple vs front)

                    2. Logo & Branding Elements:
                    - Locate and look for exact placement of "WARBY PARKER" text(if present):
                    • Side (left temple)
                    • Position from hinge (e.g., 10mm from hinge on left temple)
                    • Engraving depth and style (embossed/debossed/printed)
                    . Etch the text "WARBY PARKER" onto the left temple of the frame(if exists).
                    . The text should be embossed and in all caps.
                    . The text should be positioned 10mm from the hinge on the inside of the left temple.
                    . Rest of the temple arms should be plain (detailed textured as per the image) without any text or logo markings.

                    3. Lens Specifications:
                    - Tint gradient analysis:
                    • Gradient direction (top-bottom/left-right)
                    • Color intensity mapping (RGB values estimation)
                    . Try to extract precise color codes for the tint gradient, noting the direction and intensity of the color shift. Provide detailed information on the transition from one color to another, including the sharpness of the gradient.
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

                    need very detailed output!!!!(in more than 5 descriptive paragraphs)
                    Give the best possible explainations for colors, materials, design details and textures.
                    
                    Dont get confused with glasses body's color and the color of the lenses.
                    carefully analyze the image and provide the details of the glasses body color and the color of the lenses seperately(because lenses will mostly be transparent like this polycarbonate lenses (refractive index: 1.49) with crystal-clear transparency (0.0 color intensity),).
                    use words like "crystal-clear transparency" when lens is transparent 
                    """

    # options = webdriver.ChromeOptions() 
    # options.add_argument("user-data-dir=/Users/adityamukhopadhyay/Library/Application Support/Google/Chrome/")
    service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=options)
    driver = webdriver.Chrome(service=service)

    try:
        # Open the website
        driver.get(url)

        # Wait for the page to load completely
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Input Image URL')]"))
        )

        # Click the "Input Image URL" button
        input_url_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Input Image URL')]")
        input_url_button.click()
        print("Clicked the 'Input Image URL' button")

        # Wait for the input field to appear
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Paste your image link here']"))
        )

        # Find the input field and enter the image URL
        url_input_field = driver.find_element(By.XPATH, "//input[@placeholder='Paste your image link here']")
        url_input_field.click()
        print("Clicked the URL input field")
        url_input_field.send_keys(img_url)
        print("Entered the image URL")

        # Find and click the "Load Image URL" button
        load_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load Image URL')]")
        load_button.click()
        print("Clicked the 'Load Image URL' button")

        # Wait for the "Custom Question" button to appear
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Custom Question')]")
            )
        )

        # Click the "Custom Question" button
        custom_question_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Custom Question')]")
        custom_question_button.click()
        print("Clicked the 'Custom Question' button")

        # Wait for the textarea to appear
        WebDriverWait(driver,2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//textarea[@placeholder='e.g., What is the person doing in this image? OR Describe the setting, including the time of day, weather, and any notable objects in the scene']")
            )
        )

        # Input vision instructions
        vision_textarea = driver.find_element(
            By.XPATH,
            "//textarea[@placeholder='e.g., What is the person doing in this image? OR Describe the setting, including the time of day, weather, and any notable objects in the scene']"
        )
        vision_textarea.click()
        print("Clicked the vision textarea")
        vision_textarea.send_keys(vision_instructions)
        print("Entered the custom question")

        # Click the "Generate Description" button
        generate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate Description')]")
        generate_button.click()
        print("Clicked the 'Generate Description' button")

        # Wait for the description to be generated
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//textarea[contains(@class, 'w-full h-48')]")
            )
        )

        # Scrape the generated description
        description_textarea = driver.find_element(By.XPATH, "//textarea[contains(@class, 'w-full h-48')]")
        time.sleep(5)
        vision_analysis = description_textarea.get_attribute("value")
        print("\nExtracted vision analysis:", vision_analysis)

        # Save the vision analysis to a text file
        with open("vision_analysis.txt", "w") as file:
            file.write(vision_analysis)
        print("Saved vision analysis to 'vision_analysis.txt'")


        # Take a screenshot and save it
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to '{screenshot_path}'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # Close the WebDriver
        driver.quit()

    print(f'\n\nVison Analysis:\n{vision_analysis}\n\nProduct Details:\n{product_details}')

if os.path.exists("final_prompt.txt"):
    with open("final_prompt.txt", "r") as file:
        final_prompt = file.read()
        print(f'\n\nFinal Prompt:\n{final_prompt}')

else:

    async def generate_final_prompt():
        prompt_generator = PromptGenerator()
        final_prompt = await prompt_generator._validate_prompt(product_details, vision_analysis)
        print("\n\nFinal Prompt:\n", final_prompt)
        # Save the final prompt to a text file
        with open("final_prompt.txt", "w") as file:
            file.write(final_prompt)
        print("\n\nSaved final prompt to 'final_prompt.txt'")

    asyncio.run(generate_final_prompt())


async def process_with_rodin():
    # Load the final prompt from the text file
    with open("final_prompt.txt", "r") as file:
        final_prompt = file.read()

    # Initialize the ConfigGenerator with the LLM client
    llm_client = DeepSeekClient()
    if os.path.exists("config.json"):
        with open("config.json", "r") as file:
            config = json.load(file)
        print("\nLoaded config from 'config.json'")
    else:
        config_generator = ConfigGenerator(llm=llm_client)

        # Generate the configuration
        with open("img_list.txt", "r") as file:
            image_urls = file.read().splitlines()
        config = await config_generator.generate_config(final_prompt, image_urls)
        print("\nGenerated Rodin configuration:", config)

        # Save the generated config to a JSON file
        with open("config.json", "w") as file:
            json.dump(config, file, indent=2)
        print("\nSaved generated config to 'config.json'")

    # Initialize the ModelProcessor and process the product
    processor = ModelProcessor()
    result = processor.process_product(config)
    print("\nProcessed product at:", result)

asyncio.run(process_with_rodin())