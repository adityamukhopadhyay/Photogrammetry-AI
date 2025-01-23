import asyncio
from src.data_collection.product_scraper import WarbyScraper
from dotenv import load_dotenv
from src.llm.deepseek_client import DeepSeekClient

# add to the prompt that there's a "WARBY PARKER" text on the left temple, 25mm from the hinge in all caps, embossed style.
# the above text should be made mandoatory in the prompt, the 3D model should have the above text on the left temple, 10mm from the hinge in all caps, embossed style.
# use browser-use to pass the images to navigate to https://imageprompt.org/describe-image and upload
# the images 'input_sample_1.jpg' and 'input_sample_2.jpg' and get the description of the images.   
# return the output of the description of the images in a text file named 'visual_output.txt'
# the image_details varaible should contain the description of the images as written in the text file 'visual_output.txt'
# now for product_url = https://www.warbyparker.com scrape for the product details and return the output in a text file named 'product_output.txt'
# the product_details varaible should contain the product details as written in the text file 'product_output.txt'
# Finally combine the text from 'visual_output.txt' and 'product_output.txt' and return the final output in a text file named 'final_output.txt'    

# no images will be stored but instead the links to the images will be stored in a img_list[]
'''    def _extract_image_urls(self, soup):
        """Extract specific product image URLs from HTML"""
        images = []
        for i in [1, 4]:
            img_tag = soup.find('img', {'alt': f'PDP Thumbnail Image {i}'})
            if img_tag and img_tag.get('src'):
                images.append(img_tag['src'])
                logger.debug(f"Found PDP Thumbnail Image {i}: {img_tag['src']}")
        print(images[0]+'\n'+images[1])
        return images
'''
async def main():
    load_dotenv()
    
    # Initialize DeepSeek client
    llm_client = DeepSeekClient()
    product_url = input("Enter Warby Parker product URL: ")
    
    scraper = WarbyScraper(llm=llm_client)
    
    # Scrape the product details
    product_details = await scraper.scrape(product_url)
    
    # Print the extracted product details
    print("\n\nExtracted Product Details:")
    print(product_details)
    
    # Print the extracted image URLs
    print("\n\nExtracted Image URLs:")
    print(scraper.image_urls[0],
    scraper.image_urls[1])

if __name__ == "__main__":
    asyncio.run(main())