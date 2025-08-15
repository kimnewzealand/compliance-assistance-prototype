"""
Compliance Assistant Package
A tool for extracting compliance obligations from PDF documents.
"""

__version__ = "0.1.0"
__author__ = "Compliance Assistant Team"
__description__ = "Extract compliance obligations from PDF documents and export to Excel"

from .pdf_reader import PDFReader
from .obligation_finder import ObligationFinder
from .excel_exporter import ExcelExporter
from .main import ComplianceAssistant

__all__ = [
    "PDFReader",
    "ObligationFinder", 
    "ExcelExporter",
    "ComplianceAssistant"
]
