import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "seo_history.db")

# Default Scoring Weights (Total = 1.0)
DEFAULT_SCORING_WEIGHTS = {
    "content_length": 0.20,
    "keyword_optimization": 0.25,
    "metadata_quality": 0.20,
    "heading_structure": 0.15,
    "readability": 0.10,
    "intent_alignment": 0.10
}

# Meta Constraints
META_TITLE_MIN_LEN = 30
META_TITLE_MAX_LEN = 60
META_DESC_MIN_LEN = 120
META_DESC_MAX_LEN = 160

# Word Count Benchmarks
MIN_RECOMMENDED_WORDS = 600
OPTIMAL_WORD_COUNT_MIN = 1200
OPTIMAL_WORD_COUNT_MAX = 2500

# Keyword Density Benchmarks (%)
MIN_KEYWORD_DENSITY = 0.5
MAX_KEYWORD_DENSITY = 2.5
OPTIMAL_KEYWORD_DENSITY = 1.5

# Search Intent Categories
SEARCH_INTENTS = [
    "Informational",
    "Commercial",
    "Transactional",
    "Navigational"
]
