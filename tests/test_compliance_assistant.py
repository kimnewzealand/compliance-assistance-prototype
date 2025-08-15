"""
Unit Tests for Compliance Assistant
Tests the functionality of PDF reading, obligation finding, and Excel export.
"""

import unittest
import os
import tempfile
import shutil
import pandas as pd
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compliance_assistant.pdf_reader import PDFReader
from compliance_assistant.obligation_finder import ObligationFinder
from compliance_assistant.excel_exporter import ExcelExporter
from compliance_assistant.main import ComplianceAssistant


class TestPDFReader(unittest.TestCase):
    """Test cases for PDFReader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pdf_reader = PDFReader()
    
    def test_split_into_sentences(self):
        """Test sentence splitting functionality."""
        test_text = "This is sentence one. This is sentence two! Is this sentence three?"
        sentences = self.pdf_reader.split_into_sentences(test_text)
        
        self.assertEqual(len(sentences), 3)
        self.assertIn("This is sentence one", sentences[0])
        self.assertIn("This is sentence two", sentences[1])
        self.assertIn("Is this sentence three", sentences[2])
    
    def test_split_into_sentences_filters_short(self):
        """Test that very short sentences are filtered out."""
        test_text = "Short. This is a longer sentence that should be kept."
        sentences = self.pdf_reader.split_into_sentences(test_text)
        
        self.assertEqual(len(sentences), 1)
        self.assertIn("longer sentence", sentences[0])


class TestObligationFinder(unittest.TestCase):
    """Test cases for ObligationFinder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.finder = ObligationFinder()
    
    def test_contains_obligation_keyword(self):
        """Test obligation keyword detection."""
        self.assertTrue(self.finder.contains_obligation_keyword("Users must comply"))
        self.assertTrue(self.finder.contains_obligation_keyword("Data shall be encrypted"))
        self.assertTrue(self.finder.contains_obligation_keyword("Training is required"))
        self.assertTrue(self.finder.contains_obligation_keyword("This is mandatory"))
        self.assertFalse(self.finder.contains_obligation_keyword("This is optional"))
    
    def test_extract_obligations(self):
        """Test obligation extraction from sentences."""
        test_sentences = [
            "Users must follow security policies.",
            "This is just information.",
            "All data shall be encrypted.",
            "Regular training is required for staff."
        ]
        
        obligations = self.finder.extract_obligations(test_sentences)
        
        self.assertEqual(len(obligations), 3)
        self.assertIn("must", obligations[0]['keywords'])
        self.assertIn("shall", obligations[1]['keywords'])
        self.assertIn("required", obligations[2]['keywords'])
    
    def test_filter_obligations(self):
        """Test obligation filtering."""
        test_obligations = [
            {'text': 'Short', 'keywords': 'must'},  # Too short
            {'text': 'TITLE: SECURITY REQUIREMENTS', 'keywords': 'required'},  # All caps
            {'text': 'This is a proper obligation that must be followed by all users.', 'keywords': 'must'}
        ]
        
        filtered = self.finder.filter_obligations(test_obligations)
        
        self.assertEqual(len(filtered), 1)
        self.assertIn("proper obligation", filtered[0]['text'])


class TestExcelExporter(unittest.TestCase):
    """Test cases for ExcelExporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.exporter = ExcelExporter()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_obligation_dataframe(self):
        """Test DataFrame creation from obligations."""
        test_obligations = [
            {'text': 'Users must comply', 'keywords': 'must'},
            {'text': 'Data shall be encrypted', 'keywords': 'shall'}
        ]
        
        df = self.exporter.create_obligation_dataframe(test_obligations, 'test.pdf')
        
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['ID'], 'OBL-001')
        self.assertEqual(df.iloc[1]['ID'], 'OBL-002')
        self.assertEqual(df.iloc[0]['Source Document'], 'test.pdf')
        self.assertEqual(df.iloc[0]['Status'], 'Not Started')
    
    def test_export_to_excel(self):
        """Test Excel file export."""
        test_obligations = [
            {'text': 'Users must comply with policies', 'keywords': 'must'}
        ]
        
        output_path = os.path.join(self.temp_dir, 'test_output.xlsx')
        result_path = self.exporter.export_to_excel(test_obligations, 'test.pdf', output_path)
        
        self.assertTrue(os.path.exists(result_path))
        
        # Read back the Excel file to verify content
        df = pd.read_excel(result_path)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['ID'], 'OBL-001')
        self.assertIn('must comply', df.iloc[0]['Obligation Text'])
    
    def test_generate_output_filename(self):
        """Test output filename generation."""
        filename = self.exporter.generate_output_filename('test_document.pdf', self.temp_dir)
        
        self.assertTrue(filename.startswith(os.path.join(self.temp_dir, 'test_document_obligations_')))
        self.assertTrue(filename.endswith('.xlsx'))


class TestComplianceAssistant(unittest.TestCase):
    """Test cases for the main ComplianceAssistant class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.assistant = ComplianceAssistant()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('compliance_assistant.main.PDFReader')
    @patch('compliance_assistant.main.ObligationFinder')
    @patch('compliance_assistant.main.ExcelExporter')
    def test_process_document_success(self, mock_exporter_class, mock_finder_class, mock_reader_class):
        """Test successful document processing."""
        # Mock the components
        mock_reader = MagicMock()
        mock_finder = MagicMock()
        mock_exporter = MagicMock()
        
        mock_reader_class.return_value = mock_reader
        mock_finder_class.return_value = mock_finder
        mock_exporter_class.return_value = mock_exporter
        
        # Set up mock returns
        mock_reader.process_pdf.return_value = ['sentence 1', 'sentence 2']
        mock_finder.process_sentences.return_value = [{'text': 'obligation', 'keywords': 'must'}]
        mock_exporter.generate_output_filename.return_value = 'test_output.xlsx'
        mock_exporter.export_to_excel.return_value = 'test_output.xlsx'
        mock_exporter.create_summary_report.return_value = {
            'total_obligations': 1,
            'source_document': 'test.pdf',
            'keyword_distribution': {'must': 1},
            'extraction_timestamp': '2025-01-01T00:00:00'
        }
        
        # Create assistant with mocked components
        assistant = ComplianceAssistant()
        result = assistant.process_document('test.pdf', self.temp_dir)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['summary']['total_obligations'], 1)
        self.assertEqual(result['summary']['total_sentences'], 2)


class TestIntegration(unittest.TestCase):
    """Integration tests using the actual sample PDF."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_pdf = "data/documents/sample_IT_compliance_document.pdf"
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_full_pipeline_with_sample_pdf(self):
        """Test the complete pipeline with the sample PDF."""
        if not os.path.exists(self.sample_pdf):
            self.skipTest("Sample PDF not found")
        
        assistant = ComplianceAssistant()
        result = assistant.process_document(self.sample_pdf, self.temp_dir)
        
        self.assertTrue(result['success'])
        self.assertGreater(result['summary']['total_obligations'], 0)
        self.assertTrue(os.path.exists(result['excel_path']))
        
        # Verify Excel file content
        df = pd.read_excel(result['excel_path'])
        self.assertGreater(len(df), 0)
        self.assertIn('ID', df.columns)
        self.assertIn('Obligation Text', df.columns)
        self.assertIn('Source Document', df.columns)
        
        # Check that we found the expected number of obligations (around 5 based on manual test)
        self.assertGreaterEqual(len(df), 3)  # At least 3 obligations
        self.assertLessEqual(len(df), 10)    # But not more than 10


def run_tests():
    """Run all tests and provide a summary."""
    print("🧪 Running Compliance Assistant Unit Tests")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPDFReader))
    suite.addTests(loader.loadTestsFromTestCase(TestObligationFinder))
    suite.addTests(loader.loadTestsFromTestCase(TestExcelExporter))
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceAssistant))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
