"""
Main Script for Compliance Assistant
Combines PDF reading, obligation finding, and Excel export functionality.
"""

import os
import sys
from typing import Dict, Any

from .pdf_reader import PDFReader
from .obligation_finder import ObligationFinder
from .excel_exporter import ExcelExporter
from .logging_config import get_logger

logger = get_logger('main')


class ComplianceAssistant:
    """Main class that orchestrates the compliance obligation extraction process."""

    def __init__(self) -> None:
        """Initialize the compliance assistant with all required components."""
        logger.info("Initializing Compliance Assistant")
        self.pdf_reader = PDFReader()
        self.obligation_finder = ObligationFinder()
        self.excel_exporter = ExcelExporter()
        logger.info("Compliance Assistant initialization complete")

    def process_document(self, pdf_path: str, output_dir: str = 'output') -> Dict[str, Any]:
        """
        Process a PDF document and extract compliance obligations.

        Args:
            pdf_path: Path to the PDF document
            output_dir: Directory for output files

        Returns:
            Processing results and summary
        """
        logger.info(f"Starting document processing: {pdf_path}")

        try:
            print(f"Processing document: {pdf_path}")

            # Step 1: Extract text and split into sentences
            print("Step 1: Extracting text from PDF...")
            logger.info("Step 1: Starting PDF text extraction")
            sentences = self.pdf_reader.process_pdf(pdf_path)
            print(f"Extracted {len(sentences)} sentences")
            logger.info(f"Step 1 complete: Extracted {len(sentences)} sentences")

            # Step 2: Find compliance obligations
            print("Step 2: Finding compliance obligations...")
            logger.info("Step 2: Starting obligation detection")
            obligations = self.obligation_finder.process_sentences(sentences)
            print(f"Found {len(obligations)} compliance obligations")
            logger.info(f"Step 2 complete: Found {len(obligations)} obligations")

            # Step 3: Export to Excel
            print("Step 3: Exporting to Excel...")
            logger.info("Step 3: Starting Excel export")
            source_document = os.path.basename(pdf_path)
            output_path = self.excel_exporter.generate_output_filename(source_document, output_dir)
            excel_path = self.excel_exporter.export_to_excel(obligations, source_document, output_path)
            print(f"Excel file created: {excel_path}")
            logger.info(f"Step 3 complete: Excel file created at {excel_path}")

            # Step 4: Generate summary
            logger.info("Step 4: Generating summary report")
            summary = self.excel_exporter.create_summary_report(obligations, source_document)
            summary['excel_output_path'] = excel_path
            summary['total_sentences'] = len(sentences)

            result = {
                'success': True,
                'summary': summary,
                'obligations': obligations,
                'excel_path': excel_path
            }

            logger.info("Document processing completed successfully")
            return result

        except Exception as e:
            error_msg = f"Error processing document: {str(e)}"
            logger.error(f"Document processing failed: {error_msg}")
            print(f"ERROR: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

    def print_summary(self, result: Dict[str, Any]) -> None:
        """
        Print a formatted summary of the processing results.

        Args:
            result: Processing results
        """
        logger.debug("Printing summary report")

        if not result['success']:
            print(f"\n❌ Processing failed: {result['error']}")
            logger.warning(f"Processing failed: {result['error']}")
            return

        summary = result['summary']

        print("\n" + "="*60)
        print("📋 COMPLIANCE ASSISTANT SUMMARY")
        print("="*60)
        print(f"📄 Source Document: {summary['source_document']}")
        print(f"📊 Total Sentences: {summary['total_sentences']}")
        print(f"⚖️ Total Obligations: {summary['total_obligations']}")
        print(f"📁 Excel Output: {summary['excel_output_path']}")

        if summary['keyword_distribution']:
            print(f"\n🔍 Keyword Distribution:")
            for keyword, count in summary['keyword_distribution'].items():
                print(f"   • {keyword}: {count}")

        print(f"\n⏰ Processed at: {summary['extraction_timestamp']}")
        print("="*60)

        # Show first few obligations as preview
        if result['obligations']:
            print("\n📝 Sample Obligations (first 3):")
            for i, obligation in enumerate(result['obligations'][:3], 1):
                text = obligation['text']
                if len(text) > 100:
                    text = text[:97] + "..."
                print(f"   {i}. [{obligation['keywords']}] {text}")

            if len(result['obligations']) > 3:
                print(f"   ... and {len(result['obligations']) - 3} more obligations")

        logger.debug("Summary report printed successfully")


def main() -> None:
    """Main function to run the compliance assistant."""
    logger.info("Starting Compliance Assistant main function")

    print("🚀 Compliance Assistant - PDF Obligation Extractor")
    print("="*60)

    # Default PDF path
    default_pdf = "data/documents/sample_IT_compliance_document.pdf"

    # Check if PDF exists
    if not os.path.exists(default_pdf):
        error_msg = f"Sample PDF not found at {default_pdf}"
        logger.error(error_msg)
        print(f"❌ Error: {error_msg}")
        print("Please ensure the sample PDF is in the correct location.")
        sys.exit(1)

    logger.info(f"Using PDF file: {default_pdf}")

    # Initialize and run the compliance assistant
    assistant = ComplianceAssistant()
    result = assistant.process_document(default_pdf)

    # Print summary
    assistant.print_summary(result)

    if result['success']:
        print(f"\n✅ Processing completed successfully!")
        print(f"📁 Check the output folder for your Excel file: {result['excel_path']}")
        logger.info("Main function completed successfully")
    else:
        print(f"\n❌ Processing failed. Please check the error message above.")
        logger.error("Main function failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
