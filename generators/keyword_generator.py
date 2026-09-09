from typing import Dict, Any, List
from analyzer.keyword_analyzer import KeywordAnalyzer

class KeywordGenerator:
    """Generates keyword opportunities, LSI suggestions, and search-intent categories."""

    def __init__(self):
        self.analyzer = KeywordAnalyzer()

    def generate_keyword_strategy(self, content_text: str, target_keyword: str = "") -> Dict[str, Any]:
        """Generates primary keywords, secondary LSI keywords, and intent opportunities."""
        extracted = self.analyzer.extract_keywords(content_text, top_n=20)

        primary_kw = target_keyword if target_keyword else (extracted[0]["keyword"] if extracted else "SEO Content")
        
        secondary_keywords = [
            kw for kw in extracted 
            if kw["keyword"].lower() != primary_kw.lower()
        ]

        # Opportunities: high relevance terms with 0 or low density
        missing_lsi = []
        lsi_candidates = [
            f"{primary_kw} guide", f"{primary_kw} best practices", f"{primary_kw} tools",
            f"{primary_kw} strategy", f"{primary_kw} optimization", f"how to use {primary_kw}",
            f"{primary_kw} examples", f"{primary_kw} tutorial"
        ]

        content_lower = content_text.lower()
        for cand in lsi_candidates:
            if cand.lower() not in content_lower:
                missing_lsi.append(cand)

        # Categorize intent opportunities
        intent_groups = {
            "Informational": [],
            "Commercial": [],
            "Transactional": [],
            "Navigational": []
        }
        for kw in extracted:
            intent_groups[kw["intent"]].append(kw["keyword"])

        return {
            "primary_keyword": primary_kw,
            "secondary_keywords": secondary_keywords[:10],
            "missing_lsi_opportunities": missing_lsi[:6],
            "intent_distribution": intent_groups
        }
