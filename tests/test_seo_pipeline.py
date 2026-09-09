# Tests for the SEO Automation Platform
import unittest
import os
import json

# Ensure the project root is in PYTHONPATH for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from extractor.content_extractor import ContentExtractor
from analyzer.keyword_analyzer import KeywordAnalyzer
from analyzer.content_analyzer import ContentAnalyzer
from analyzer.seo_scorer import SEOScorer
from llm.llm_service import LLMService
from generators.meta_generator import MetaGenerator
from generators.keyword_generator import KeywordGenerator
from generators.heading_generator import HeadingGenerator
from generators.content_optimizer import ContentOptimizer
from recommendations.recommendation_engine import RecommendationEngine

class TestSEOAutomationPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize shared services
        cls.extractor = ContentExtractor()
        cls.kw_analyzer = KeywordAnalyzer()
        cls.content_analyzer = ContentAnalyzer()
        cls.scorer = SEOScorer()
        cls.llm = LLMService()  # No API key; will use fallback heuristics
        cls.meta_gen = MetaGenerator(cls.llm)
        cls.kw_gen = KeywordGenerator()
        cls.heading_gen = HeadingGenerator(cls.llm)
        cls.optimizer = ContentOptimizer(cls.llm)
        cls.recommendation_engine = RecommendationEngine()

        # Sample text for testing (simple paragraph with heading markdown)
        cls.sample_text = """# Sample SEO Guide\n\nSearch engine optimization (SEO) is essential for online visibility.\n\n## Why SEO Matters\nGood SEO practices improve organic traffic and increase conversions.\n\n## Key Strategies\n- Keyword research\n- Quality content creation\n- Technical site health\n"""
        cls.sample_url = "https://example.com"
        cls.target_keyword = "SEO"

    def test_content_extractor_from_text(self):
        result = self.extractor.extract_from_text(self.sample_text, title="Sample SEO Guide", description="A brief guide on SEO.")
        self.assertTrue(result["success"])
        self.assertIn("headings", result)
        self.assertGreaterEqual(result["word_count"], 10)

    def test_keyword_extraction(self):
        keywords = self.kw_analyzer.extract_keywords(self.sample_text, top_n=5)
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 5)
        # Ensure target keyword appears in extracted list (or fallback)
        kw_texts = [kw["keyword"] for kw in keywords]
        self.assertTrue(any(self.target_keyword.lower() in k.lower() for k in kw_texts))

    def test_content_readability(self):
        readability = self.content_analyzer.analyze_readability(self.sample_text)
        self.assertIn("flesch_reading_ease", readability)
        self.assertGreaterEqual(readability["word_count"], 10)

    def test_seo_scoring(self):n        target_analysis = self.kw_analyzer.analyze_target_keyword(
            self.sample_text, self.target_keyword, meta_title="SEO Guide", meta_description="Learn SEO.", headings=[]
        )
        heading_analysis = self.content_analyzer.analyze_heading_structure([])
        readability = self.content_analyzer.analyze_readability(self.sample_text)
        score = self.scorer.calculate_score(
            word_count=readability["word_count"],
            target_kw_analysis=target_analysis,
            meta_title="SEO Guide",
            meta_description="Learn SEO.",
            heading_analysis=heading_analysis,
            readability_analysis=readability
        )
        self.assertIn("overall_score", score)
        self.assertGreaterEqual(score["overall_score"], 0)
        self.assertLessEqual(score["overall_score"], 100)

    def test_meta_generator(self):
        meta = self.meta_gen.generate(self.sample_text, self.target_keyword)
        self.assertIn("title_options", meta)
        self.assertIn("description_options", meta)
        self.assertTrue(all(isinstance(t["title"], str) for t in meta["title_options"]))
        self.assertTrue(all(isinstance(d["description"], str) for d in meta["description_options"]))

    def test_keyword_generator(self):
        strategy = self.kw_gen.generate_keyword_strategy(self.sample_text, self.target_keyword)
        self.assertIn("primary_keyword", strategy)
        self.assertIn("secondary_keywords", strategy)
        self.assertIn("missing_lsi_opportunities", strategy)

    def test_heading_generator(self):
        outline = self.heading_gen.generate_recommended_outline(self.sample_text, self.target_keyword)
        self.assertIsInstance(outline, list)
        self.assertTrue(all("level" in h and "text" in h for h in outline))

    def test_content_optimizer(self):
        # Use empty headings list for original; optimizer will generate its own
        result = self.optimizer.optimize_and_compare(
            original_text=self.sample_text,
            target_keyword=self.target_keyword,
            missing_keywords=["keyword research", "on-page optimization"],
            original_meta_title="SEO Guide",
            original_meta_desc="Learn SEO.",
            original_headings=[]
        )
        self.assertIn("original_text", result)
        self.assertIn("optimized_text", result)
        self.assertIn("comparison", result)
        self.assertGreater(result["comparison"]["after_score"], 0)

    def test_recommendation_engine(self):
        # Use known values to provoke some warnings
        heading_analysis = self.content_analyzer.analyze_heading_structure([])
        readability = self.content_analyzer.analyze_readability(self.sample_text)
        media_analysis = self.content_analyzer.analyze_media_and_links([], {"internal": 0, "external": 0})
        target_analysis = self.kw_analyzer.analyze_target_keyword(
            self.sample_text, self.target_keyword, meta_title="", meta_description="", headings=[]
        )
        recs = self.recommendation_engine.generate_recommendations(
            word_count=readability["word_count"],
            target_kw_analysis=target_analysis,
            meta_title="",
            meta_description="",
            heading_analysis=heading_analysis,
            readability_analysis=readability,
            media_analysis=media_analysis
        )
        self.assertIn("issues", recs)
        self.assertIn("recommendations", recs)
        self.assertGreaterEqual(len(recs["issues"]), 1)

if __name__ == "__main__":
    unittest.main()
