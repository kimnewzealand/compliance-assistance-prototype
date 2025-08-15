"""
Command Line Interface for Compliance Assistant
Entry point for running the compliance assistant from command line.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

from .main import ComplianceAssistant
from .logging_config import setup_logging, get_logger


def main() -> None:
    """Main CLI entry point."""
    # Set up logging first
    setup_logging(log_level="INFO", console_output=False)  # Only log to file for CLI
    logger = get_logger('cli')

    logger.info("Starting CLI application")

    parser = argparse.ArgumentParser(
        description="Extract compliance obligations from PDF documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Process default sample PDF
  %(prog)s --pdf path/to/document.pdf        # Process specific PDF
  %(prog)s --output /custom/output/dir       # Use custom output directory
        """
    )

    parser.add_argument(
        '--pdf',
        type=str,
        default="data/documents/sample_IT_compliance_document.pdf",
        help='Path to PDF document to process (default: sample document)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default="output",
        help='Output directory for Excel files (default: output)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )

    args = parser.parse_args()

    # Update logging level if specified
    if args.log_level != 'INFO':
        setup_logging(log_level=args.log_level, console_output=False)
        logger = get_logger('cli')

    logger.info(f"CLI arguments: pdf={args.pdf}, output={args.output}, log_level={args.log_level}")

    # Validate PDF file exists
    if not os.path.exists(args.pdf):
        error_msg = f"PDF file not found: {args.pdf}"
        logger.error(error_msg)
        print(f"❌ Error: {error_msg}")
        sys.exit(1)

    # Run the compliance assistant
    print("🚀 Compliance Assistant - PDF Obligation Extractor")
    print("="*60)

    try:
        assistant = ComplianceAssistant()
        result = assistant.process_document(args.pdf, args.output)

        # Print summary
        assistant.print_summary(result)

        if result['success']:
            print(f"\n✅ Processing completed successfully!")
            print(f"📁 Check the output folder for your Excel file: {result['excel_path']}")
            logger.info("CLI application completed successfully")
            sys.exit(0)
        else:
            print(f"\n❌ Processing failed. Please check the error message above.")
            logger.error("CLI application failed during processing")
            sys.exit(1)

    except Exception as e:
        error_msg = f"Unexpected error in CLI: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
