from typing import Dict, Any, List
from config import META_TITLE_MIN_LEN, META_TITLE_MAX_LEN, META_DESC_MIN_LEN, META_DESC_MAX_LEN, MIN_RECOMMENDED_WORDS, MIN_KEYWORD_DENSITY, MAX_KEYWORD_DENSITY

class RecommendationEngine:
    """Detects basic and advanced SEO issues and outputs prioritized actionable recommendations."""

    def generate_recommendations(
        self,
        word_count: int,
        target_kw_analysis: Dict[str, Any],
        meta_title: str,
        meta_description: str,
        heading_analysis: Dict[str, Any],
        readability_analysis: Dict[str, Any],
        media_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates categorized issues (Critical, Warning, Info) and actionable fix steps."""

        issues = []
        recommendations = []

        # 1. Meta Title Audits
        title_str = meta_title.strip() if meta_title else ""
        if not title_str:
            issues.append({
                "severity": "Critical",
                "category": "Metadata",
                "message": "Missing Meta Title tag.",
                "solution": "Add a unique Meta Title between 50-60 characters containing your primary target keyword."
            })
            recommendations.append("Priority 1: Create a compelling Meta Title (50-60 chars) including the primary keyword.")
        else:
            title_len = len(title_str)
            if title_len < META_TITLE_MIN_LEN or title_len > META_TITLE_MAX_LEN:
                issues.append({
                    "severity": "Warning",
                    "category": "Metadata",
                    "message": f"Meta Title length ({title_len} chars) is outside optimal range ({META_TITLE_MIN_LEN}-{META_TITLE_MAX_LEN} chars).",
                    "solution": "Adjust title length to avoid SERP truncation or low CTR."
                })
                recommendations.append(f"Adjust Meta Title length to 50-60 characters (currently {title_len} chars).")

        # 2. Meta Description Audits
        desc_str = meta_description.strip() if meta_description else ""
        if not desc_str:
            issues.append({
                "severity": "Critical",
                "category": "Metadata",
                "message": "Missing Meta Description tag.",
                "solution": "Add a Meta Description between 140-160 characters with a strong Call-To-Action (CTA)."
            })
            recommendations.append("Priority 1: Add an engaging Meta Description (140-160 chars) with CTA and target keyword.")
        else:
            desc_len = len(desc_str)
            if desc_len < META_DESC_MIN_LEN or desc_len > META_DESC_MAX_LEN:
                issues.append({
                    "severity": "Warning",
                    "category": "Metadata",
                    "message": f"Meta Description length ({desc_len} chars) is outside optimal range ({META_DESC_MIN_LEN}-{META_DESC_MAX_LEN} chars).",
                    "solution": "Keep meta descriptions between 140-160 characters for complete search snippet visibility."
                })

        # 3. Target Keyword Coverage
        target_kw = target_kw_analysis.get("target_keyword", "")
        if target_kw:
            if not target_kw_analysis.get("in_title"):
                issues.append({
                    "severity": "Critical",
                    "category": "Keyword Optimization",
                    "message": f"Target keyword '{target_kw}' is missing from the Meta Title.",
                    "solution": "Place the target keyword near the beginning of the Meta Title."
                })
                recommendations.append(f"Include exact target keyword '{target_kw}' in the Meta Title.")

            if not target_kw_analysis.get("in_h1"):
                issues.append({
                    "severity": "Critical",
                    "category": "Keyword Optimization",
                    "message": f"Target keyword '{target_kw}' is missing from the H1 main heading.",
                    "solution": "Include the target keyword inside your page H1 heading tag."
                })
                recommendations.append(f"Add target keyword '{target_kw}' into the main H1 heading.")

            density = target_kw_analysis.get("density_pct", 0.0)
            if density < MIN_KEYWORD_DENSITY:
                issues.append({
                    "severity": "Warning",
                    "category": "Keyword Density",
                    "message": f"Low keyword density ({density}%). Recommended: {MIN_KEYWORD_DENSITY}% - {MAX_KEYWORD_DENSITY}%.",
                    "solution": "Naturally integrate the target keyword throughout body paragraphs and subheadings."
                })
                recommendations.append(f"Increase keyword density for '{target_kw}' to around 1.0% - 2.0% (currently {density}%).")
            elif density > MAX_KEYWORD_DENSITY:
                issues.append({
                    "severity": "Warning",
                    "category": "Keyword Stuffing",
                    "message": f"Keyword density ({density}%) is overly high (potential keyword stuffing).",
                    "solution": "Reduce repetitive exact-match keyword usage and replace with semantic LSI synonyms."
                })
                recommendations.append(f"Reduce exact keyword repetition for '{target_kw}' to prevent search engine penalty.")

        # 4. Heading Structure Audits
        h1_count = heading_analysis.get("h1_count", 0)
        if h1_count == 0:
            issues.append({
                "severity": "Critical",
                "category": "Heading Structure",
                "message": "Page is missing an H1 tag.",
                "solution": "Add exactly one H1 tag defining the primary topic of the page."
            })
        elif h1_count > 1:
            issues.append({
                "severity": "Warning",
                "category": "Heading Structure",
                "message": f"Multiple H1 tags detected ({h1_count}).",
                "solution": "Use only 1 main H1 per page and demote secondary titles to H2."
            })

        for h_issue in heading_analysis.get("heading_issues", []):
            if "Skipped" in h_issue:
                issues.append({
                    "severity": "Warning",
                    "category": "Heading Hierarchy",
                    "message": h_issue,
                    "solution": "Maintain sequential heading levels (H1 -> H2 -> H3) without skipping ranks."
                })

        # 5. Content Length & Readability Audits
        if word_count < 300:
            issues.append({
                "severity": "Critical",
                "category": "Content Depth",
                "message": f"Thin Content detected ({word_count} words).",
                "solution": "Expand content to at least {MIN_RECOMMENDED_WORDS} words to provide thorough value for search intent."
            })
            recommendations.append(f"Expand thin content ({word_count} words) to at least 600+ words with detailed subtopics.")
        elif word_count < MIN_RECOMMENDED_WORDS:
            issues.append({
                "severity": "Warning",
                "category": "Content Depth",
                "message": f"Content length ({word_count} words) is below recommended benchmark ({MIN_RECOMMENDED_WORDS}+ words).",
                "solution": "Add comprehensive sections, examples, FAQs, or step-by-step instructions."
            })

        fre = readability_analysis.get("flesch_reading_ease", 0.0)
        if fre < 40 and word_count > 50:
            issues.append({
                "severity": "Warning",
                "category": "Readability",
                "message": f"Content readability score is low (Flesch score: {fre}).",
                "solution": "Shorten long sentences, split dense paragraphs, and use simpler vocabulary."
            })
            recommendations.append("Improve readability by breaking down long complex sentences into shorter paragraphs.")

        # 6. Media & Link Opportunities
        if media_analysis.get("missing_alt_count", 0) > 0:
            issues.append({
                "severity": "Info",
                "category": "Image Accessibility & SEO",
                "message": f"{media_analysis['missing_alt_count']} images are missing descriptive alt attributes.",
                "solution": "Add descriptive image alt attributes containing context or relevant keywords."
            })
            recommendations.append("Add descriptive alt tags to all images for image search ranking and accessibility.")

        if media_analysis.get("internal_links", 0) == 0:
            issues.append({
                "severity": "Info",
                "category": "Internal Linking",
                "message": "No internal links detected in the content.",
                "solution": "Add 2-4 contextual internal links pointing to relevant pages or articles on your domain."
            })

        return {
            "issues": issues,
            "recommendations": recommendations,
            "critical_count": sum(1 for i in issues if i["severity"] == "Critical"),
            "warning_count": sum(1 for i in issues if i["severity"] == "Warning"),
            "info_count": sum(1 for i in issues if i["severity"] == "Info")
        }
