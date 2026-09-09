from typing import Dict, Any, List
from llm.llm_service import LLMService
from config import META_TITLE_MIN_LEN, META_TITLE_MAX_LEN, META_DESC_MIN_LEN, META_DESC_MAX_LEN

class MetaGenerator:
    """Generates and evaluates SEO-optimized Meta Titles and Meta Descriptions."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def generate(self, content_text: str, target_keyword: str) -> Dict[str, Any]:
        """Generates title and description recommendations with character count analysis."""
        titles = self.llm.generate_meta_titles(content_text, target_keyword)
        descriptions = self.llm.generate_meta_descriptions(content_text, target_keyword)

        evaluated_titles = [self.evaluate_title(t, target_keyword) for t in titles]
        evaluated_descriptions = [self.evaluate_description(d, target_keyword) for d in descriptions]

        return {
            "title_options": evaluated_titles,
            "best_title": evaluated_titles[0] if evaluated_titles else None,
            "description_options": evaluated_descriptions,
            "best_description": evaluated_descriptions[0] if evaluated_descriptions else None
        }

    def evaluate_title(self, title: str, target_keyword: str) -> Dict[str, Any]:
        char_count = len(title.strip())
        is_optimal = META_TITLE_MIN_LEN <= char_count <= META_TITLE_MAX_LEN
        has_keyword = target_keyword.lower() in title.lower() if target_keyword else True

        status = "Optimal" if is_optimal and has_keyword else ("Too Short" if char_count < META_TITLE_MIN_LEN else "Too Long")

        return {
            "title": title,
            "char_count": char_count,
            "is_optimal_length": is_optimal,
            "has_keyword": has_keyword,
            "status": status
        }

    def evaluate_description(self, description: str, target_keyword: str) -> Dict[str, Any]:
        char_count = len(description.strip())
        is_optimal = META_DESC_MIN_LEN <= char_count <= META_DESC_MAX_LEN
        has_keyword = target_keyword.lower() in description.lower() if target_keyword else True

        status = "Optimal" if is_optimal and has_keyword else ("Too Short" if char_count < META_DESC_MIN_LEN else "Too Long")

        return {
            "description": description,
            "char_count": char_count,
            "is_optimal_length": is_optimal,
            "has_keyword": has_keyword,
            "status": status
        }
