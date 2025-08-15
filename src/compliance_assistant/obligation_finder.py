"""
Obligation Finder Module for Compliance Assistant
Finds compliance obligations in text using keyword matching.
"""

import re
from typing import List, Dict
from .logging_config import get_logger

logger = get_logger('obligation_finder')


class ObligationFinder:
    """Finds compliance obligations in text using keyword patterns."""

    # Keywords that typically indicate compliance obligations
    OBLIGATION_KEYWORDS: List[str] = ['must', 'shall', 'required', 'mandatory']

    def __init__(self) -> None:
        """Initialize the obligation finder."""
        logger.info("Initializing obligation finder")
        logger.debug(f"Using obligation keywords: {self.OBLIGATION_KEYWORDS}")
        pass
    
    def contains_obligation_keyword(self, sentence: str) -> bool:
        """
        Check if a sentence contains any obligation keywords.

        Args:
            sentence: The sentence to check

        Returns:
            True if sentence contains obligation keywords
        """
        sentence_lower = sentence.lower()

        for keyword in self.OBLIGATION_KEYWORDS:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sentence_lower):
                logger.debug(f"Found keyword '{keyword}' in sentence: {sentence[:50]}...")
                return True

        return False
    
    def extract_obligations(self, sentences: List[str]) -> List[Dict[str, str]]:
        """
        Extract obligation sentences from a list of sentences.

        Args:
            sentences: List of sentences to analyze

        Returns:
            List of obligation dictionaries with text and keywords
        """
        logger.info(f"Starting obligation extraction from {len(sentences)} sentences")
        obligations = []

        for i, sentence in enumerate(sentences):
            if self.contains_obligation_keyword(sentence):
                # Find which keywords are present
                found_keywords = []
                sentence_lower = sentence.lower()

                for keyword in self.OBLIGATION_KEYWORDS:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, sentence_lower):
                        found_keywords.append(keyword)

                obligation = {
                    'text': sentence.strip(),
                    'keywords': ', '.join(found_keywords)
                }
                obligations.append(obligation)
                logger.debug(f"Found obligation {len(obligations)}: {sentence[:50]}...")

        logger.info(f"Extracted {len(obligations)} potential obligations")
        return obligations
    
    def filter_obligations(self, obligations: List[Dict[str, str]],
                          min_length: int = 20) -> List[Dict[str, str]]:
        """
        Filter obligations by minimum length and other criteria.

        Args:
            obligations: List of obligation dictionaries
            min_length: Minimum length for obligation text

        Returns:
            Filtered list of obligations
        """
        logger.info(f"Starting filtering of {len(obligations)} obligations")
        filtered = []
        filtered_count = 0

        for obligation in obligations:
            text = obligation['text']

            # Filter by minimum length
            if len(text) < min_length:
                logger.debug(f"Filtered out obligation (too short): {text[:30]}...")
                filtered_count += 1
                continue

            # Filter out common false positives (headers, titles, etc.)
            if text.isupper() and len(text) < 100:  # Skip all-caps short text
                logger.debug(f"Filtered out obligation (all caps): {text[:30]}...")
                filtered_count += 1
                continue

            # Skip sentences that are mostly numbers or special characters
            alpha_chars = sum(c.isalpha() for c in text)
            if alpha_chars < len(text) * 0.5:  # Less than 50% alphabetic
                logger.debug(f"Filtered out obligation (non-alphabetic): {text[:30]}...")
                filtered_count += 1
                continue

            filtered.append(obligation)

        logger.info(f"Filtering complete: {len(filtered)} obligations kept, {filtered_count} filtered out")
        return filtered
    
    def process_sentences(self, sentences: List[str]) -> List[Dict[str, str]]:
        """
        Complete obligation processing: extract and filter obligations.

        Args:
            sentences: List of sentences to process

        Returns:
            List of filtered obligation dictionaries
        """
        logger.info(f"Starting complete obligation processing for {len(sentences)} sentences")

        obligations = self.extract_obligations(sentences)
        filtered_obligations = self.filter_obligations(obligations)

        logger.info(f"Obligation processing complete: {len(filtered_obligations)} final obligations")
        return filtered_obligations


def main() -> None:
    """Test the obligation finder with sample sentences."""
    logger.info("Starting obligation finder test")
    finder = ObligationFinder()

    # Test sentences
    test_sentences = [
        "Users must comply with all security policies.",
        "The system shall encrypt all data in transit.",
        "Regular backups are recommended for data safety.",
        "Access to sensitive data is required to be logged.",
        "This is a mandatory training session for all employees.",
        "Please review the documentation.",
        "TITLE: SECURITY REQUIREMENTS",  # Should be filtered out
        "123-456-789 must be updated"  # Should be filtered out
    ]

    print("Testing Obligation Finder...")
    obligations = finder.process_sentences(test_sentences)

    print(f"\nFound {len(obligations)} obligations:")
    for i, obligation in enumerate(obligations, 1):
        print(f"{i}. Keywords: [{obligation['keywords']}]")
        print(f"   Text: {obligation['text']}")
        print()

    logger.info("Obligation finder test completed successfully")


if __name__ == "__main__":
    main()
