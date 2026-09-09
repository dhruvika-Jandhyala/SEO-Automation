import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from typing import Dict, Any, List

class ContentExtractor:
    """
    Extracts structured content, metadata, headings, images, and links from URLs,
    raw article text, or topic prompts.
    """
    
    def __init__(self, user_agent: str = None):
        self.headers = {
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SEOAutomationBot/1.0"
        }

    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Fetches web page and extracts full content, headings, meta tags, and images."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            response = requests.get(url, headers=self.headers, timeout=12)
            response.raise_for_status()
            html_content = response.text
            return self.parse_html(html_content, source_url=url)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract from URL: {str(e)}",
                "source_url": url,
                "raw_text": "",
                "meta_title": "",
                "meta_description": "",
                "headings": [],
                "images": [],
                "links": {"internal": 0, "external": 0},
                "canonical": ""
            }

    def parse_html(self, html_content: str, source_url: str = "") -> Dict[str, Any]:
        """Parses HTML document to extract metadata, headings, and clean text."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script, style, and navigation noise
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()

        # Meta Title
        title_tag = soup.find("title")
        meta_title = title_tag.get_text(strip=True) if title_tag else ""
        og_title = soup.find("meta", property="og:title")
        if not meta_title and og_title:
            meta_title = og_title.get("content", "")

        # Meta Description
        meta_desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
        meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""

        # Canonical URL
        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag.get("href", "") if canonical_tag else ""

        # Headings
        headings: List[Dict[str, str]] = []
        for tag in soup.find_all(re.compile(r"^h[1-6]$", re.I)):
            level = tag.name.upper()
            text = tag.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})

        # Images & Alt tags
        images: List[Dict[str, str]] = []
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "").strip()
            images.append({"src": src, "alt": alt})

        # Links
        internal_links = 0
        external_links = 0
        domain = urlparse(source_url).netloc if source_url else ""

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if source_url and domain:
                link_domain = urlparse(href).netloc
                if not link_domain or link_domain == domain:
                    internal_links += 1
                else:
                    external_links += 1
            else:
                if href.startswith("http"):
                    external_links += 1
                else:
                    internal_links += 1

        # Text Extraction
        paragraphs = [p.get_text(strip=True) for p in soup.find_all(["p", "li", "article"]) if p.get_text(strip=True)]
        raw_text = "\n\n".join(paragraphs)

        if not raw_text.strip():
            raw_text = soup.get_text(separator="\n", strip=True)

        return {
            "success": True,
            "source_url": source_url,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "canonical": canonical,
            "headings": headings,
            "images": images,
            "links": {"internal": internal_links, "external": external_links},
            "raw_text": raw_text,
            "word_count": len(re.findall(r"\w+", raw_text))
        }

    def extract_from_text(self, text: str, title: str = "", description: str = "") -> Dict[str, Any]:
        """Processes raw text/article content directly."""
        clean_text = text.strip()

        # Regex detect headings like '# Heading' or '## Heading'
        headings = []
        lines = clean_text.split("\n")
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("# "):
                headings.append({"level": "H1", "text": line_str[2:].strip()})
            elif line_str.startswith("## "):
                headings.append({"level": "H2", "text": line_str[3:].strip()})
            elif line_str.startswith("### "):
                headings.append({"level": "H3", "text": line_str[4:].strip()})

        # If no markdown headings, check for short title-like lines
        if not title and lines:
            first_line = lines[0].strip()
            if len(first_line) < 80 and not first_line.endswith("."):
                title = first_line

        return {
            "success": True,
            "source_url": "",
            "meta_title": title,
            "meta_description": description,
            "canonical": "",
            "headings": headings,
            "images": [],
            "links": {"internal": 0, "external": 0},
            "raw_text": clean_text,
            "word_count": len(re.findall(r"\w+", clean_text))
        }

    def extract_from_topic(self, topic: str) -> Dict[str, Any]:
        """Creates a baseline project structure for a new topic prompt."""
        topic_clean = topic.strip()
        return {
            "success": True,
            "source_url": "",
            "meta_title": f"Complete Guide to {topic_clean.title()}",
            "meta_description": f"Learn everything about {topic_clean}. Key strategies, actionable tips, and expert recommendations.",
            "canonical": "",
            "headings": [
                {"level": "H1", "text": f"Ultimate Guide to {topic_clean.title()}"},
                {"level": "H2", "text": f"What is {topic_clean.title()}?"},
                {"level": "H2", "text": f"Key Benefits of {topic_clean.title()}"},
                {"level": "H2", "text": "Best Practices and Step-by-Step Tutorial"},
                {"level": "H2", "text": "Conclusion"}
            ],
            "images": [],
            "links": {"internal": 0, "external": 0},
            "raw_text": f"{topic_clean}. This content topic focuses on providing comprehensive insights, actionable guidance, best practices, and strategies.",
            "word_count": 25
        }
