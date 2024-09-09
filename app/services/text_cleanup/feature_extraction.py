import pandas as pd


# TODO: Find common words that are in disclaimer pages but not in other pages.
from collections import Counter

KEYWORDS_DISCLAIMER_PAGE_DETECTION = [
    "disclaimer",
    "information",
    "tax",
    "sales",
    "deferred",
    "charge",
]

# TODO: Add keywords that are in other pages but not in disclaimer pages.

KEYWORDS_NON_DISCLAIMER_PAGE_DETECTION = ["quantity", "price", "$"]


def count_total_keyword_occurrences(words: list[str], keywords: list[str]) -> int:
    return sum(word in keywords for word in words)


def count_keywords(words: list[str], keywords: list[str]) -> dict[str, int]:
    counter = Counter(word for word in words if word in keywords)
    return counter


class LineFeatureExtractor:
    def __init__(self):
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def extract_features(self) -> pd.DataFrame:
        """
        Extracts features from the lines added to the LineFeatureExtractor.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted features.
        """
        features = []
        for line in self.lines:
            features.append(self.extract_features_from_line(line))

        return pd.DataFrame(features)

    def extract_features_from_line(self, line):
        """
        Extracts features from a single line.

        Args:
            line: The line to extract features from.
        """
        pass


class PageFeatureExtractor:
    def __init__(self):
        self.pages: list[str] = []
        self.words: list[list[str]] = []
        self.pages_word_count = []

    def add_page(self, page: str):
        self.pages.append(page.strip().lower())
        words = page.split()
        self.words.append(words)
        self.pages_word_count.append(len(words))

    def extract_features(self) -> pd.DataFrame:
        """
        Extracts features from the pages added to the PageFeatureExtractor.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted features.
        """
        features = []
        for page in self.pages:
            features.append(self.extract_features_from_page(page))

        return pd.DataFrame(features)

    def extract_features_from_page(self, page_index: int):
        """
        Extracts features from a single page.

        Args:
            page: The page to extract features from.

        Returns:
            dict: A dictionary containing the extracted features.
        """
        page_text = self.pages[page_index]
        page_word_count = self.pages_word_count[page_index]
        words = self.words[page_index]
        features = {
            "distance_from_start": page_index,
            "distance_from_end": len(self.pages) - page_index,
            "page_word_count_ratio": page_word_count / sum(self.pages_word_count),
            "disclaimer_keyword_ratio": count_total_keyword_occurrences(
                words, KEYWORDS_DISCLAIMER_PAGE_DETECTION
            )
            / page_word_count
            if page_word_count > 0
            else 0,
            "non_disclaimer_keyword_ratio": count_total_keyword_occurrences(
                words, KEYWORDS_NON_DISCLAIMER_PAGE_DETECTION
            )
            / page_word_count
            if page_word_count > 0
            else 0,
            "digit_count_ratio": sum(char.isdigit() for char in page_text)
            / page_word_count
            if page_word_count > 0
            else 0,
        }
        return features
