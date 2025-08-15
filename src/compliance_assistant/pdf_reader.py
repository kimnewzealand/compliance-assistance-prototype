"""
PDF Reader Module for Compliance Assistant
Extracts text from PDF documents and splits into sentences.
"""

import pypdf
import re
from typing import List
from .logging_config import get_logger

logger = get_logger('pdf_reader')


class PDFReader:
    """Simple PDF reader that extracts text and splits into sentences."""

    def __init__(self) -> None:
        """Initialize the PDF reader."""
        logger.info("Initializing PDF reader")
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text from the PDF

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF cannot be read
        """
        logger.info(f"Starting text extraction from PDF: {pdf_path}")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""

                logger.debug(f"PDF has {len(pdf_reader.pages)} pages")

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    logger.debug(f"Extracted {len(page_text)} characters from page {page_num + 1}")

                extracted_text = text.strip()
                logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
                return extracted_text

        except FileNotFoundError as e:
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}") from e
        except Exception as e:
            logger.error(f"Error reading PDF file {pdf_path}: {str(e)}")
            raise Exception(f"Error reading PDF file: {str(e)}") from e
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using basic regex patterns.

        Args:
            text: Input text to split

        Returns:
            List of sentences
        """
        logger.debug(f"Starting sentence splitting for text of length {len(text)}")

        # Clean up the text - remove extra whitespace and line breaks
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        logger.debug(f"Text cleaned, length: {len(cleaned_text)}")

        # Split into sentences using periods, exclamation marks, and question marks
        # Look for sentence endings followed by whitespace and capital letters
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, cleaned_text)
        logger.debug(f"Initial split produced {len(sentences)} potential sentences")

        # Clean up sentences - remove empty ones and strip whitespace
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Filter out very short fragments
                cleaned_sentences.append(sentence)

        logger.info(f"Split text into {len(cleaned_sentences)} valid sentences")
        return cleaned_sentences
    
    def process_pdf(self, pdf_path: str) -> List[str]:
        """
        Complete PDF processing: extract text and split into sentences.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of sentences from the PDF
        """
        logger.info(f"Starting complete PDF processing for: {pdf_path}")

        text = self.extract_text_from_pdf(pdf_path)
        sentences = self.split_into_sentences(text)

        logger.info(f"PDF processing complete. Extracted {len(sentences)} sentences")
        return sentences


def main() -> None:
    """Test the PDF reader with the sample document."""
    logger.info("Starting PDF reader test")
    pdf_reader = PDFReader()

    try:
        # Test with sample document
        pdf_path = "data/documents/sample_IT_compliance_document.pdf"
        sentences = pdf_reader.process_pdf(pdf_path)

        print(f"Successfully extracted {len(sentences)} sentences from PDF")
        print("\nFirst 3 sentences:")
        for i, sentence in enumerate(sentences[:3], 1):
            print(f"{i}. {sentence[:100]}...")

        logger.info("PDF reader test completed successfully")

    except Exception as e:
        logger.error(f"PDF reader test failed: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
