import re
from collections import Counter
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "also", "can", "will", "just", "like", "get", "use", "make", "one", "way"
])

class KeywordAnalyzer:
    """Analyzes keyword density, TF-IDF weights, search intent, and target keyword usage."""

    def extract_keywords(self, text: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Extracts top single and multi-word keywords using TF-IDF and Frequency."""
        clean_text = text.lower()
        words = re.findall(r"\b[a-z]{3,}\b", clean_text)
        filtered_words = [w for w in words if w not in STOPWORDS]

        if not filtered_words:
            return []

        word_counts = Counter(filtered_words)
        total_words = max(len(words), 1)

        # TF-IDF extraction for 1-gram, 2-gram, 3-gram
        try:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                stop_words='english',
                max_features=top_n * 2
            )
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            keywords = []
            for phrase, score in zip(feature_names, scores):
                if score > 0:
                    phrase_count = len(re.findall(r"\b" + re.escape(phrase) + r"\b", clean_text))
                    density = round((phrase_count * len(phrase.split()) / total_words) * 100, 2)
                    intent = self.classify_search_intent(phrase)
                    keywords.append({
                        "keyword": phrase,
                        "tfidf_score": round(float(score), 4),
                        "count": phrase_count,
                        "density_pct": density,
                        "intent": intent
                    })

            keywords.sort(key=lambda x: (x["tfidf_score"], x["count"]), reverse=True)
            return keywords[:top_n]
        except Exception:
            # Fallback frequency extraction
            keywords = []
            for word, count in word_counts.most_common(top_n):
                density = round((count / total_words) * 100, 2)
                keywords.append({
                    "keyword": word,
                    "tfidf_score": round(count / len(filtered_words), 4),
                    "count": count,
                    "density_pct": density,
                    "intent": self.classify_search_intent(word)
                })
            return keywords

    def classify_search_intent(self, keyword: str) -> str:
        """Classifies keyword into Search Intent Category."""
        kw = keyword.lower()
        if any(w in kw for w in ["buy", "order", "price", "pricing", "cheap", "cost", "discount", "coupon", "purchase", "shop"]):
            return "Transactional"
        elif any(w in kw for w in ["best", "top", "review", "vs", "compare", "comparison", "alternative", "guide", "rating"]):
            return "Commercial"
        elif any(w in kw for w in ["login", "signin", "portal", "website", "app", "official", "support"]):
            return "Navigational"
        else:
            return "Informational"

    def analyze_target_keyword(self, text: str, target_keyword: str, meta_title: str = "", meta_description: str = "", headings: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Analyzes target keyword placement across key SEO locations."""
        if not target_keyword:
            return {
                "target_keyword": "",
                "in_title": False,
                "in_meta_desc": False,
                "in_h1": False,
                "in_headings_count": 0,
                "occurrences": 0,
                "density_pct": 0.0,
                "status": "No target keyword specified."
            }

        tk = target_keyword.lower().strip()
        text_lower = text.lower()
        words = re.findall(r"\w+", text_lower)
        total_words = max(len(words), 1)

        # Exact match count
        tk_regex = r"\b" + re.escape(tk) + r"\b"
        occurrences = len(re.findall(tk_regex, text_lower))
        tk_word_len = len(tk.split())
        density = round((occurrences * tk_word_len / total_words) * 100, 2)

        in_title = bool(re.search(tk_regex, meta_title.lower())) if meta_title else False
        in_meta_desc = bool(re.search(tk_regex, meta_description.lower())) if meta_description else False

        in_h1 = False
        in_headings_count = 0
        if headings:
            for h in headings:
                if re.search(tk_regex, h.get("text", "").lower()):
                    in_headings_count += 1
                    if h.get("level") == "H1":
                        in_h1 = True

        return {
            "target_keyword": target_keyword,
            "in_title": in_title,
            "in_meta_desc": in_meta_desc,
            "in_h1": in_h1,
            "in_headings_count": in_headings_count,
            "occurrences": occurrences,
            "density_pct": density,
            "intent": self.classify_search_intent(target_keyword)
        }
