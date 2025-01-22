from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
import json

class ProductSpecs(BaseModel):
    material: str = Field(..., description="Frame material composition")
    lens_type: str = Field(..., description="Type of lenses")
    measurements: dict = Field(..., description="Dimensions in mm format")
    branding: list[str] = Field(..., description="All branding elements")
    features: list[str] = Field(..., description="Special features")

class WarbyScraper:
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ProductSpecs)
        
    async def scrape(self, url):
        loader = AsyncHtmlLoader([url])
        docs = await loader.load()
        
        transformer = Html2TextTransformer()
        transformed = transformer.transform_documents(docs)
        
        prompt = f"""Extract product specs from this page content:
        {transformed[0].page_content}
        
        {self.parser.get_format_instructions()}"""
        
        result = await self.llm.ainvoke(prompt)
        return self.parser.parse(result.content)