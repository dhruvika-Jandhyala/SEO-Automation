from typing import Dict, Any, List
from llm.llm_service import LLMService

class HeadingGenerator:
    """Generates structured H1, H2, H3 content outlines tailored to SEO search intent."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def generate_recommended_outline(self, content_text: str, target_keyword: str) -> List[Dict[str, str]]:
        """Generates an SEO-optimized heading outline."""
        return self.llm.generate_outline(content_text, target_keyword)
