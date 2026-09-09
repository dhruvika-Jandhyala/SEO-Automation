from typing import Dict, Any
from config import (
    DEFAULT_SCORING_WEIGHTS, META_TITLE_MIN_LEN, META_TITLE_MAX_LEN,
    META_DESC_MIN_LEN, META_DESC_MAX_LEN, MIN_RECOMMENDED_WORDS,
    OPTIMAL_WORD_COUNT_MIN, MIN_KEYWORD_DENSITY, MAX_KEYWORD_DENSITY
)

class SEOScorer:
    """Computes a multi-criteria weighted 0-100 SEO score with breakdown metrics."""

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_SCORING_WEIGHTS

    def calculate_score(
        self,
        word_count: int,
        target_kw_analysis: Dict[str, Any],
        meta_title: str,
        meta_description: str,
        heading_analysis: Dict[str, Any],
        readability_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculates individual pillar scores and overall weighted SEO score."""

        # 1. Content Length Score (0-100)
        if word_count >= OPTIMAL_WORD_COUNT_MIN:
            length_score = 100.0
        elif word_count >= MIN_RECOMMENDED_WORDS:
            length_score = 75.0 + (word_count - MIN_RECOMMENDED_WORDS) / (OPTIMAL_WORD_COUNT_MIN - MIN_RECOMMENDED_WORDS) * 25.0
        elif word_count > 0:
            length_score = (word_count / MIN_RECOMMENDED_WORDS) * 70.0
        else:
            length_score = 0.0

        # 2. Metadata Quality Score (0-100)
        meta_score = 0.0
        title_len = len(meta_title.strip()) if meta_title else 0
        desc_len = len(meta_description.strip()) if meta_description else 0

        # Title evaluation (50 pts max)
        if META_TITLE_MIN_LEN <= title_len <= META_TITLE_MAX_LEN:
            meta_score += 40.0
        elif title_len > 0:
            meta_score += 20.0
        if target_kw_analysis.get("in_title"):
            meta_score += 10.0

        # Description evaluation (50 pts max)
        if META_DESC_MIN_LEN <= desc_len <= META_DESC_MAX_LEN:
            meta_score += 40.0
        elif desc_len > 0:
            meta_score += 20.0
        if target_kw_analysis.get("in_meta_desc"):
            meta_score += 10.0

        # 3. Keyword Optimization Score (0-100)
        kw_score = 0.0
        density = target_kw_analysis.get("density_pct", 0.0)
        target_kw = target_kw_analysis.get("target_keyword", "")

        if target_kw:
            if MIN_KEYWORD_DENSITY <= density <= MAX_KEYWORD_DENSITY:
                kw_score += 40.0
            elif density > 0:
                kw_score += 20.0

            if target_kw_analysis.get("in_title"):
                kw_score += 20.0
            if target_kw_analysis.get("in_h1"):
                kw_score += 20.0
            if target_kw_analysis.get("in_meta_desc"):
                kw_score += 20.0
        else:
            # If no specific target keyword was defined, score based on general TF-IDF density
            kw_score = 75.0

        # 4. Heading Structure Score (0-100)
        heading_score = 100.0
        if heading_analysis.get("h1_count") != 1:
            heading_score -= 35.0
        if heading_analysis.get("h2_count") == 0:
            heading_score -= 25.0
        issues_count = len(heading_analysis.get("heading_issues", []))
        heading_score = max(0.0, heading_score - (issues_count * 10.0))

        # 5. Readability Score (0-100)
        fre = readability_analysis.get("flesch_reading_ease", 0.0)
        if fre >= 60:
            readability_score = 100.0
        elif fre >= 40:
            readability_score = 75.0
        elif fre > 0:
            readability_score = 50.0
        else:
            readability_score = 30.0

        # 6. Intent Alignment Score (0-100)
        intent = target_kw_analysis.get("intent", "Informational")
        intent_score = 90.0 if intent else 70.0

        # Weighted Total Score
        total_score = (
            (length_score * self.weights.get("content_length", 0.20)) +
            (kw_score * self.weights.get("keyword_optimization", 0.25)) +
            (meta_score * self.weights.get("metadata_quality", 0.20)) +
            (heading_score * self.weights.get("heading_structure", 0.15)) +
            (readability_score * self.weights.get("readability", 0.10)) +
            (intent_score * self.weights.get("intent_alignment", 0.10))
        )

        total_score = round(min(100.0, max(0.0, total_score)), 1)

        return {
            "overall_score": total_score,
            "breakdown": {
                "content_length": round(length_score, 1),
                "keyword_optimization": round(kw_score, 1),
                "metadata_quality": round(meta_score, 1),
                "heading_structure": round(heading_score, 1),
                "readability": round(readability_score, 1),
                "intent_alignment": round(intent_score, 1)
            }
        }
