import textstat
import re
from typing import Dict, Any, List

class ContentAnalyzer:
    """Analyzes text readability, heading hierarchy, link counts, image alt attributes, and thin content issues."""

    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """Calculates Flesch Reading Ease, Grade Level, and readability metrics."""
        if not text or len(text.strip()) < 20:
            return {
                "flesch_reading_ease": 0.0,
                "flesch_grade_level": 0.0,
                "readability_label": "Very Poor",
                "avg_sentence_length": 0,
                "word_count": 0
            }

        try:
            fre = textstat.flesch_reading_ease(text)
            fkgl = textstat.flesch_kincaid_grade(text)
        except Exception:
            fre = 60.0
            fkgl = 8.0

        if fre >= 80:
            label = "Very Easy"
        elif fre >= 70:
            label = "Easy"
        elif fre >= 60:
            label = "Standard / Fair"
        elif fre >= 50:
            label = "Fairly Difficult"
        elif fre >= 30:
            label = "Difficult"
        else:
            label = "Very Confusing"

        words = re.findall(r"\w+", text)
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        avg_sent_len = round(len(words) / max(len(sentences), 1), 1)

        return {
            "flesch_reading_ease": round(fre, 1),
            "flesch_grade_level": round(fkgl, 1),
            "readability_label": label,
            "avg_sentence_length": avg_sent_len,
            "word_count": len(words)
        }

    def analyze_heading_structure(self, headings: List[Dict[str, str]]) -> Dict[str, Any]:
        """Audits H1-H6 heading hierarchy for proper structure and missing tags."""
        h1_list = [h for h in headings if h.get("level") == "H1"]
        h2_list = [h for h in headings if h.get("level") == "H2"]
        h3_list = [h for h in headings if h.get("level") == "H3"]

        issues = []
        if len(h1_list) == 0:
            issues.append("Missing H1 tag. Every page should have exactly one main H1 heading.")
        elif len(h1_list) > 1:
            issues.append(f"Multiple H1 tags found ({len(h1_list)}). Recommended to use only 1 H1 per page.")

        if len(h2_list) == 0 and len(headings) > 1:
            issues.append("No H2 section headings found. Organize content with clear H2 headings.")

        # Check for skipped levels e.g. H1 -> H3
        prev_level = 0
        for h in headings:
            lvl_num = int(h.get("level", "H1")[1])
            if prev_level > 0 and lvl_num - prev_level > 1:
                issues.append(f"Skipped heading level from H{prev_level} directly to H{lvl_num} ('{h.get('text')[:30]}...').")
            prev_level = lvl_num

        return {
            "h1_count": len(h1_list),
            "h2_count": len(h2_list),
            "h3_count": len(h3_list),
            "total_headings": len(headings),
            "heading_issues": issues,
            "has_h1": len(h1_list) == 1,
            "is_structured": len(issues) == 0
        }

    def analyze_media_and_links(self, images: List[Dict[str, str]], links: Dict[str, int]) -> Dict[str, Any]:
        """Audits image alt attributes and internal/external links."""
        total_images = len(images)
        missing_alt = sum(1 for img in images if not img.get("alt", "").strip())

        return {
            "total_images": total_images,
            "missing_alt_count": missing_alt,
            "has_alt_issues": missing_alt > 0,
            "internal_links": links.get("internal", 0),
            "external_links": links.get("external", 0)
        }
