import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import gemini_service

class TestGeminiService(unittest.TestCase):
    """Test suite for Gemini service functions"""

    @patch('app.services.gemini_service.GenerativeModel')
    def test_generate_answer(self, mock_model):
        """Test generate_answer function"""
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = "This is a test answer."
        mock_model.return_value = mock_instance

        answer = gemini_service.generate_answer("What is a test?")

        self.assertEqual(answer, "This is a test answer.")
        mock_instance.generate_content.assert_called_with("What is a test?")

    @patch('app.services.gemini_service.retrieve_context')
    @patch('app.services.gemini_service.GenerativeModel')
    def test_generate_answer_with_context(self, mock_model, mock_retrieve_context):
        """Test generate_answer_with_context function"""
        mock_retrieve_context.return_value = (["This is context."], ["source1.pdf"])
        
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = "This is a context-aware answer."
        mock_model.return_value = mock_instance

        answer, sources = gemini_service.generate_answer_with_context("What is a test?", "corpus_id")

        self.assertEqual(answer, "This is a context-aware answer.")
        self.assertEqual(sources, ["source1.pdf"])
        mock_retrieve_context.assert_called_with("corpus_id", "What is a test?", 10, 0.4)

    @patch('builtins.open')
    @patch('app.services.gemini_service.mimetypes.guess_type')
    @patch('app.services.gemini_service.GenerativeModel')
    def test_summarize_file(self, mock_model, mock_guess_type, mock_open):
        """Test summarize_file function"""
        mock_guess_type.return_value = ('application/pdf', None)
        
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = "This is a file summary."
        mock_model.return_value = mock_instance

        summary = gemini_service.summarize_file('/fake/path/file.pdf')

        self.assertEqual(summary, "This is a file summary.")
        mock_open.assert_called_with('/fake/path/file.pdf', 'rb')

    @patch('app.services.gemini_service.GenerativeModel')
    def test_generate_suggested_questions(self, mock_model):
        """Test generate_suggested_questions function"""
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = "Question 1?\nQuestion 2?"
        mock_model.return_value = mock_instance
        
        questions = gemini_service.generate_suggested_questions("Test Topic")
        
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0], "Question 1?")
        self.assertEqual(questions[1], "Question 2?")

if __name__ == '__main__':
    unittest.main()
