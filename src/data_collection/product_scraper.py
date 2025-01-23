import logging
from typing import List
logger = logging.getLogger(__name__)
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from playwright.async_api import async_playwright
import asyncio

class ProductSpecs(BaseModel):
    material: str = Field(..., description="Frame material composition")
    lens_type: str = Field(..., description="Type of lenses")
    measurements: dict = Field(..., description="Dimensions in mm format")
    branding: list[str] = Field(..., description="All branding elements")
    features: list[str] = Field(..., description="Special features")
    roughness: float = Field(0.4, description="Material roughness 0-1")
    metallic: float = Field(0.0, description="Metallic property 0-1")
    ior: float = Field(1.49, description="Index of refraction")

class WarbyScraper:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ProductSpecs)
        self.browser_settings = {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "viewport": {"width": 1920, "height": 1080},
            "java_script_enabled": True
        }
        self.image_urls = []  # New list to store image URLs

    def _extract_image_urls(self, soup):
        """Extract specific product image URLs from HTML"""
        images = []
        for i in [1, 4]:
            img_tag = soup.find('img', {'alt': f'PDP Thumbnail Image {i}'})
            if img_tag and img_tag.get('src'):
                images.append(img_tag['src'])
                logger.debug(f"Found PDP Thumbnail Image {i}: {img_tag['src']}")

        return images

    def _create_documents(self, html_content, source_url):
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract image URLs and store in instance variable
        self.image_urls = self._extract_image_urls(soup)
        logger.info(f"Extracted {len(self.image_urls)} product images")
        
        return [
            Document(
                page_content=soup.get_text(separator=" ", strip=True),
                metadata={
                    "source": source_url,
                    "image_urls": self.image_urls  # Store in metadata
                }
            )
        ]

    async def scrape(self, url):
        logger.info(f"🔄 Starting scrape for URL: {url}")
        try:
            content = await self._get_rendered_content(url)
            logger.debug("✅ Successfully rendered page content")
            
            docs = self._create_documents(content, url)
            logger.debug(f"📄 Created {len(docs)} document(s)")
            
            transformed = self._transform_documents(docs)
            self._log_transformed_content(transformed)  # New logging
            
            return await self._process_content(transformed[0].page_content)
        except Exception as e:
            logger.error(f"🔥 Scrape failed: {str(e)}")
            raise

    def _log_transformed_content(self, transformed_docs: List[Document]):
        """Log transformed content for debugging"""
        logger.debug("📝 Transformed Content Preview:")
        for i, doc in enumerate(transformed_docs[:1]):  # First doc only
            content_preview = doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content
            logger.debug(f"Document {i+1}:\n{'-'*50}\n{content_preview}\n{'-'*50}")

    async def _get_rendered_content(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(**self.browser_settings)
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                content = await page.content()
            finally:
                await browser.close()
            
            return content

    # def _create_documents(self, html_content, source_url):
    #     soup = BeautifulSoup(html_content, "html.parser")
    #     return [
    #         Document(
    #             page_content=soup.get_text(separator=" ", strip=True),
    #             metadata={"source": source_url}
    #         )
    #     ]

    def _transform_documents(self, docs):
        return Html2TextTransformer().transform_documents(docs)

    async def _process_content(self, page_content):
        prompt = f"""Extract and structure ONLY the following information from the product description:

        Required Information(if available):
        1. Frame Material (composition and finish):
        2. Lens Type (material and optical properties):
        3. Precise Measurements (numerical values in mm):
        4. Branding Elements (logos, engravings):
        5. Technical Features (hinges, nose pads):
        6. Surface Properties (roughness 0-1):
        7. Metallic Components (0-1 scale):
        8. Lens Refractive Index:

        Formatting Rules:
        - Exclude pricing, promotions, and non-technical details
        - Use exact technical terms from the product page
        - Convert all measurements to millimeters
        - Maintain original material names

        Content to analyze:
        '''{page_content}'''

        {self.parser.get_format_instructions()}
        """
        
        result = await self.llm.ainvoke(prompt)
        return self.parser.parse(result)
