import os
import json
import re
from typing import Dict, Any, List, Optional
import google.generativeai as genai

class LLMService:
    """
    LLM Service supporting Google Gemini API with smart heuristic NLP fallback.
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.provider = provider.lower()
        self._init_client()

    def _init_client(self):
        self.has_llm = False
        if self.api_key and self.provider == "gemini":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
                self.has_llm = True
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini API client: {e}")
                self.has_llm = False

    def generate_completion(self, prompt: str, system_instruction: str = "") -> str:
        """Sends prompt to Gemini LLM or falls back if unavailable."""
        if not self.has_llm:
            return ""

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = self.model.generate_content(full_prompt)
            return response.text.strip() if response and hasattr(response, "text") else ""
        except Exception as e:
            print(f"LLM Completion Error: {e}")
            return ""

    def generate_meta_titles(self, content_snippet: str, target_keyword: str) -> List[str]:
        """Generates 3 SEO-optimized meta title options (50-60 characters)."""
        prompt = f"""
Given the following content and target keyword, generate 3 unique, high-CTR, SEO-optimized meta title variations.
- Target Keyword: '{target_keyword}'
- Content Snippet: '{content_snippet[:400]}'
- Constraint: Each title MUST be between 40 and 60 characters long.
- Include target keyword near the beginning if possible.
- Return ONLY a JSON array of 3 strings. Example: ["Title 1", "Title 2", "Title 3"]
"""
        raw_res = self.generate_completion(prompt, "You are a senior SEO Copywriter.")

        if raw_res:
            try:
                match = re.search(r"\[.*\]", raw_res, re.DOTALL)
                if match:
                    titles = json.loads(match.group(0))
                    if isinstance(titles, list) and len(titles) > 0:
                        return titles
            except Exception:
                pass

        # Smart Fallback Titles
        tk = target_keyword.title() if target_keyword else "SEO Best Practices"
        return [
            f"The Ultimate Guide to {tk} | Expert SEO Tips",
            f"How to Master {tk}: Step-by-Step Complete Guide",
            f"10 Essential {tk} Strategies for Higher Rankings"
        ]

    def generate_meta_descriptions(self, content_snippet: str, target_keyword: str) -> List[str]:
        """Generates 3 SEO-optimized meta description options (140-160 characters)."""
        prompt = f"""
Given the following content and target keyword, generate 3 unique, high-converting meta description variations.
- Target Keyword: '{target_keyword}'
- Content Snippet: '{content_snippet[:400]}'
- Constraint: Each description MUST be between 130 and 160 characters long.
- Include a strong Call to Action (CTA) and target keyword.
- Return ONLY a JSON array of 3 strings.
"""
        raw_res = self.generate_completion(prompt, "You are a senior SEO Copywriter.")

        if raw_res:
            try:
                match = re.search(r"\[.*\]", raw_res, re.DOTALL)
                if match:
                    descs = json.loads(match.group(0))
                    if isinstance(descs, list) and len(descs) > 0:
                        return descs
            except Exception:
                pass

        # Smart Fallback Descriptions
        tk = target_keyword.lower() if target_keyword else "seo strategies"
        return [
            f"Discover actionable insights on {tk}. Learn how to optimize your content, boost search rankings, and drive organic traffic today!",
            f"Looking to master {tk}? Check out our complete guide packed with expert tips, best practices, and actionable recommendations.",
            f"Unlock the full potential of {tk} with proven techniques, step-by-step strategies, and comprehensive performance metrics."
        ]

    def generate_outline(self, topic_or_text: str, target_keyword: str) -> List[Dict[str, str]]:
        """Generates an SEO-optimized heading outline (H1, H2, H3)."""
        prompt = f"""
Generate an SEO-optimized heading structure for topic/content: '{topic_or_text[:300]}'
Target Keyword: '{target_keyword}'
Format as JSON list of objects: [{"level": "H1", "text": "..."}, {"level": "H2", "text": "..."}]
"""
        raw_res = self.generate_completion(prompt, "You are an SEO Content Architect.")
        if raw_res:
            try:
                match = re.search(r"\[.*\]", raw_res, re.DOTALL)
                if match:
                    outline = json.loads(match.group(0))
                    if isinstance(outline, list):
                        return outline
            except Exception:
                pass

        # Fallback Outline
        tk = target_keyword.title() if target_keyword else "SEO Content Strategy"
        return [
            {"level": "H1", "text": f"Complete Guide to {tk}"},
            {"level": "H2", "text": f"Why {tk} Matters for Organic Growth"},
            {"level": "H2", "text": f"Core Components of Effective {tk}"},
            {"level": "H3", "text": "1. Technical Optimization & Speed"},
            {"level": "H3", "text": "2. On-Page Keyword Alignment"},
            {"level": "H2", "text": "Step-by-Step Implementation Framework"},
            {"level": "H2", "text": "Common Mistakes to Avoid"},
            {"level": "H2", "text": "Conclusion & Key Takeaways"}
        ]

    def optimize_content(self, text: str, target_keyword: str, missing_keywords: List[str]) -> str:
        """Rewrites/enhances original content incorporating target & missing keywords while preserving intent."""
        if not self.has_llm:
            return self._heuristic_content_optimizer(text, target_keyword, missing_keywords)

        missing_str = ", ".join(missing_keywords[:5]) if missing_keywords else "none"
        prompt = f"""
Rewrite and optimize the following content for search engines:
- Target Keyword: '{target_keyword}'
- Missing LSI Keywords to integrate naturally: {missing_str}
- Guidelines: Preserve original message/intent, improve readability, add H2 headers if missing, fix spelling/grammar, and maintain a natural keyword density (1.5%).

Original Content:
{text[:2500]}
"""
        raw_res = self.generate_completion(prompt, "You are an expert SEO Content Editor.")
        return raw_res if raw_res and len(raw_res) > 50 else self._heuristic_content_optimizer(text, target_keyword, missing_keywords)

    def _heuristic_content_optimizer(self, text: str, target_keyword: str, missing_keywords: List[str]) -> str:
        """Fallback content optimizer when LLM API key is not supplied."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return f"# Complete Guide to {target_keyword.title()}\n\nContent optimization requires text."

        optimized_lines = []

        # Ensure H1 tag header exists
        if not lines[0].startswith("# "):
            optimized_lines.append(f"# Ultimate Guide to {target_keyword.title()}\n")

        kw_inserted = False
        for i, line in enumerate(lines):
            optimized_lines.append(line)
            # Inject an H2 header if long block
            if i == len(lines) // 2 and len(lines) > 2:
                optimized_lines.append(f"\n## Key Strategies for {target_keyword.title()}\n")

        # Append missing keyword context paragraph if any missing
        if missing_keywords:
            kw_addon = ", ".join(missing_keywords[:4])
            optimized_lines.append(f"\n## Related Insights & Key Terminology\nWhen implementing {target_keyword}, it is vital to consider relevant industry factors including {kw_addon}. Addressing these areas ensures thorough content coverage and aligns directly with user search intent.")

        return "\n\n".join(optimized_lines)
