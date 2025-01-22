from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_community.document_transformers import Html2TextTransformer
from playwright.async_api import async_playwright
import asyncio

async def test_web_scraping():
    """Test website scraping with browser emulation"""
    test_url = "https://www.warbyparker.com/eyeglasses/brimmer/black-walnut"
    
    print(f"\nTesting scraping for URL: {test_url}")
    
    # Configure browser headers and settings
    browser_settings = {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "java_script_enabled": True
    }
    
    # Use Playwright for JavaScript rendering
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(**browser_settings)
        page = await context.new_page()
        
        # Load page with browser-like behavior
        await page.goto(test_url, wait_until="networkidle")
        content = await page.content()
        
        # Save to temporary file for processing
        temp_path = "/tmp/scraped_page.html"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Read and parse HTML content directly
        with open(temp_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Create Document
        docs = [
            Document(
                page_content=soup.get_text(separator=" ", strip=True),
                metadata={"source": test_url}
            )
        ]
        await browser.close()
    
    # Rest of processing remains the same
    transformer = Html2TextTransformer()
    transformed_docs = transformer.transform_documents(docs)
    extracted_content = transformed_docs[0].page_content

    # Validate content
    assert len(extracted_content) > 0, "No content extracted!"
    assert "Warby Parker" in extracted_content
    
    print("\nSuccessfully extracted content:")
    print("-" * 50)
    print(extracted_content[:500] + "...")
    print("-" * 50)
    return True

if __name__ == "__main__":
    asyncio.run(test_web_scraping())
    print("\nTest passed!")