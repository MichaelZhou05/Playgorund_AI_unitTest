import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import rag_service

class TestRagService(unittest.TestCase):
    """Test suite for RAG service functions"""

    @patch('app.services.rag_service.rag.create_corpus')
    @patch('app.services.rag_service.rag.import_files')
    def test_create_and_provision_corpus(self, mock_import_files, mock_create_corpus):
        """Test create_and_provision_corpus function"""
        # Mock the rag.create_corpus call
        mock_corpus = MagicMock()
        mock_corpus.name = "corpora/test_corpus"
        mock_create_corpus.return_value = mock_corpus

        files_to_upload = [
            {'id': '1', 'display_name': 'file1.pdf', 'gcs_uri': 'gs://bucket/file1.pdf'},
            {'id': '2', 'display_name': 'file2.pdf', 'gcs_uri': 'gs://bucket/file2.pdf'},
        ]

        corpus_name = rag_service.create_and_provision_corpus(files_to_upload)

        self.assertEqual(corpus_name, "corpora/test_corpus")
        mock_create_corpus.assert_called_once()
        self.assertEqual(mock_import_files.call_count, 2)


    @patch('app.services.rag_service.rag.retrieval_query')
    def test_retrieve_context(self, mock_retrieval_query):
        """Test retrieve_context function"""
        # Mock the rag.retrieval_query call
        mock_response = MagicMock()
        
        mock_context1 = MagicMock()
        mock_context1.text = "This is context 1."
        mock_context1.source_uri = "gs://bucket/file1.pdf"
        mock_context1.distance = 0.1

        mock_context2 = MagicMock()
        mock_context2.text = "This is context 2."
        mock_context2.source_uri = "gs://bucket/file2.pdf"
        mock_context2.distance = 0.2

        mock_response.contexts.contexts = [mock_context1, mock_context2]
        mock_retrieval_query.return_value = mock_response

        contexts, sources = rag_service.retrieve_context("corpus_id", "What is a test?")

        self.assertEqual(len(contexts), 2)
        self.assertEqual(len(sources), 2)
        self.assertEqual(contexts[0], "This is context 1.")
        self.assertEqual(sources[0]['filename'], "file1.pdf")

if __name__ == '__main__':
    unittest.main()
