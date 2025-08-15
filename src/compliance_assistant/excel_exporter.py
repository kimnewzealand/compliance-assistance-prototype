"""
Excel Exporter Module for Compliance Assistant
Exports compliance obligations to Excel format.
"""

import pandas as pd
import os
from typing import List, Dict, Any
from datetime import datetime
from .logging_config import get_logger

logger = get_logger('excel_exporter')


class ExcelExporter:
    """Exports compliance obligations to Excel format."""

    def __init__(self) -> None:
        """Initialize the Excel exporter."""
        logger.info("Initializing Excel exporter")
        pass
    
    def create_obligation_dataframe(self, obligations: List[Dict[str, str]],
                                  source_document: str) -> pd.DataFrame:
        """
        Create a pandas DataFrame from obligations list.

        Args:
            obligations: List of obligation dictionaries
            source_document: Name of the source document

        Returns:
            DataFrame with obligation data
        """
        logger.info(f"Creating DataFrame for {len(obligations)} obligations from {source_document}")
        data = []

        for i, obligation in enumerate(obligations, 1):
            row = {
                'ID': f'OBL-{i:03d}',  # Format as OBL-001, OBL-002, etc.
                'Obligation Text': obligation['text'],
                'Source Document': source_document,
                'Keywords': obligation.get('keywords', ''),
                'Owner': 'Not Started',
                'Next Due Date': 'Not Started',
                'Status': 'Not Started'
            }
            data.append(row)
            logger.debug(f"Added obligation {i}: {obligation['text'][:50]}...")

        df = pd.DataFrame(data)
        logger.info(f"DataFrame created with {len(df)} rows and {len(df.columns)} columns")
        return df
    
    def format_excel_worksheet(self, df: pd.DataFrame, worksheet: Any) -> None:
        """
        Apply formatting to the Excel worksheet.

        Args:
            df: The DataFrame with data
            worksheet: The openpyxl worksheet object
        """
        logger.debug("Starting Excel worksheet formatting")

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    logger.debug(f"Error calculating cell length: {e}")
                    pass

            # Set column width with some padding
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
            logger.debug(f"Set column {column_letter} width to {adjusted_width}")

        # Make header row bold
        for cell in worksheet[1]:
            from openpyxl.styles import Font
            cell.font = Font(bold=True)

        logger.debug("Excel worksheet formatting completed")
    
    def export_to_excel(self, obligations: List[Dict[str, str]],
                       source_document: str, output_path: str) -> str:
        """
        Export obligations to Excel file.

        Args:
            obligations: List of obligation dictionaries
            source_document: Name of the source document
            output_path: Path where Excel file should be saved

        Returns:
            Full path to the created Excel file
        """
        logger.info(f"Starting Excel export to: {output_path}")

        # Create DataFrame
        df = self.create_obligation_dataframe(obligations, source_document)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_dir}")

        # Export to Excel with formatting
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Compliance Obligations', index=False)

                # Get the worksheet for formatting
                worksheet = writer.sheets['Compliance Obligations']
                self.format_excel_worksheet(df, worksheet)

            logger.info(f"Successfully exported {len(obligations)} obligations to Excel: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}")
            raise
    
    def generate_output_filename(self, source_document: str, output_dir: str = 'output') -> str:
        """
        Generate a timestamped output filename.

        Args:
            source_document: Name of the source document
            output_dir: Output directory

        Returns:
            Full path for the output file
        """
        # Extract base name without extension
        base_name = os.path.splitext(os.path.basename(source_document))[0]

        # Add timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{base_name}_obligations_{timestamp}.xlsx'

        full_path = os.path.join(output_dir, filename)
        logger.debug(f"Generated output filename: {full_path}")
        return full_path
    
    def create_summary_report(self, obligations: List[Dict[str, str]],
                            source_document: str) -> Dict[str, Any]:
        """
        Create a summary report of the extraction process.

        Args:
            obligations: List of obligation dictionaries
            source_document: Name of the source document

        Returns:
            Summary statistics
        """
        logger.info(f"Creating summary report for {len(obligations)} obligations")
        keyword_counts: Dict[str, int] = {}

        for obligation in obligations:
            keywords = obligation.get('keywords', '').split(', ')
            for keyword in keywords:
                if keyword.strip():
                    keyword_counts[keyword.strip()] = keyword_counts.get(keyword.strip(), 0) + 1

        summary = {
            'total_obligations': len(obligations),
            'source_document': source_document,
            'keyword_distribution': keyword_counts,
            'extraction_timestamp': datetime.now().isoformat()
        }

        logger.debug(f"Summary report created: {summary}")
        return summary


def main() -> None:
    """Test the Excel exporter with sample data."""
    logger.info("Starting Excel exporter test")
    exporter = ExcelExporter()

    # Sample obligations data
    sample_obligations = [
        {
            'text': 'Users must comply with all security policies and procedures.',
            'keywords': 'must'
        },
        {
            'text': 'All data transfers shall be encrypted using approved protocols.',
            'keywords': 'shall'
        },
        {
            'text': 'Regular security training is required for all employees.',
            'keywords': 'required'
        }
    ]

    # Test export
    output_path = exporter.generate_output_filename('sample_document.pdf')
    result_path = exporter.export_to_excel(sample_obligations, 'sample_document.pdf', output_path)

    print(f"Test Excel file created: {result_path}")

    # Test summary
    summary = exporter.create_summary_report(sample_obligations, 'sample_document.pdf')
    print(f"Summary: {summary}")

    logger.info("Excel exporter test completed successfully")


if __name__ == "__main__":
    main()
