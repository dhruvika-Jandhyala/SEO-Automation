from typing import Dict, Any, List
from llm.llm_service import LLMService
from analyzer.content_analyzer import ContentAnalyzer
from analyzer.keyword_analyzer import KeywordAnalyzer
from analyzer.seo_scorer import SEOScorer

class ContentOptimizer:
    """Optimizes content using AI/NLP rules while preserving original intent and comparing before-and-after metrics."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.content_analyzer = ContentAnalyzer()
        self.keyword_analyzer = KeywordAnalyzer()
        self.scorer = SEOScorer()

    def optimize_and_compare(
        self,
        original_text: str,
        target_keyword: str,
        missing_keywords: List[str],
        original_meta_title: str,
        original_meta_desc: str,
        original_headings: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generates AI optimized content and returns comparative metrics (before vs after)."""

        # 1. Evaluate Original Content Metrics
        orig_readability = self.content_analyzer.analyze_readability(original_text)
        orig_kw_analysis = self.keyword_analyzer.analyze_target_keyword(
            original_text, target_keyword, original_meta_title, original_meta_desc, original_headings
        )
        orig_heading_analysis = self.content_analyzer.analyze_heading_structure(original_headings)
        orig_score = self.scorer.calculate_score(
            orig_readability["word_count"], orig_kw_analysis, original_meta_title, original_meta_desc,
            orig_heading_analysis, orig_readability
        )

        # 2. Generate Optimized Content
        optimized_text = self.llm.optimize_content(original_text, target_keyword, missing_keywords)

        # 3. Evaluate Optimized Content Metrics
        opt_readability = self.content_analyzer.analyze_readability(optimized_text)

        # Extract headings from optimized markdown text
        opt_headings = []
        for line in optimized_text.split("\n"):
            line_str = line.strip()
            if line_str.startswith("# "):
                opt_headings.append({"level": "H1", "text": line_str[2:].strip()})
            elif line_str.startswith("## "):
                opt_headings.append({"level": "H2", "text": line_str[3:].strip()})
            elif line_str.startswith("### "):
                opt_headings.append({"level": "H3", "text": line_str[4:].strip()})

        # Generate recommended meta title & desc for optimized version
        opt_meta_title = f"{target_keyword.title()}: Complete Guide & Expert Tips" if target_keyword else original_meta_title
        opt_meta_desc = f"Learn how to master {target_keyword.lower()} with our complete, step-by-step guide. Explore best practices and optimize performance today!" if target_keyword else original_meta_desc

        opt_kw_analysis = self.keyword_analyzer.analyze_target_keyword(
            optimized_text, target_keyword, opt_meta_title, opt_meta_desc, opt_headings
        )
        opt_heading_analysis = self.content_analyzer.analyze_heading_structure(opt_headings)
        opt_score = self.scorer.calculate_score(
            opt_readability["word_count"], opt_kw_analysis, opt_meta_title, opt_meta_desc,
            opt_heading_analysis, opt_readability
        )

        return {
            "original_text": original_text,
            "optimized_text": optimized_text,
            "comparison": {
                "before_score": orig_score["overall_score"],
                "after_score": opt_score["overall_score"],
                "score_delta": round(opt_score["overall_score"] - orig_score["overall_score"], 1),
                "before_word_count": orig_readability["word_count"],
                "after_word_count": opt_readability["word_count"],
                "before_density": orig_kw_analysis["density_pct"],
                "after_density": opt_kw_analysis["density_pct"],
                "before_readability": orig_readability["flesch_reading_ease"],
                "after_readability": opt_readability["flesch_reading_ease"],
                "before_headings_count": len(original_headings),
                "after_headings_count": len(opt_headings),
                "before_breakdown": orig_score["breakdown"],
                "after_breakdown": opt_score["breakdown"]
            }
        }
