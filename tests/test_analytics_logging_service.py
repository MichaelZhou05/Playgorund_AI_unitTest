import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import analytics_logging_service

class TestAnalyticsLoggingService(unittest.TestCase):
    """Test suite for Analytics Logging service functions"""

    @patch('app.services.analytics_logging_service.firestore_service')
    @patch('app.services.analytics_logging_service.gemini_service')
    def test_log_chat_query(self, mock_gemini_service, mock_firestore_service):
        """Test log_chat_query function"""
        mock_gemini_service.get_embedding.return_value = [0.1, 0.2, 0.3]
        mock_firestore_service.log_analytics_event.return_value = "doc_id_123"

        doc_id = analytics_logging_service.log_chat_query(
            course_id="course1",
            query_text="What is a test?",
            answer_text="An answer.",
            sources=["source1.pdf"]
        )

        self.assertEqual(doc_id, "doc_id_123")
        mock_gemini_service.get_embedding.assert_called_with(
            text="What is a test?",
            model_name="text-embedding-004",
            task_type="RETRIEVAL_QUERY"
        )
        
        # Get the call arguments from the mock
        call_args = mock_firestore_service.log_analytics_event.call_args[0][0]
        
        # Assertions on the logged data
        self.assertEqual(call_args['type'], 'chat')
        self.assertEqual(call_args['course_id'], 'course1')
        self.assertEqual(call_args['query_text'], 'What is a test?')
        self.assertEqual(call_args['query_vector'], [0.1, 0.2, 0.3])


    @patch('app.services.analytics_logging_service.firestore_service')
    def test_log_kg_node_click(self, mock_firestore_service):
        """Test log_kg_node_click function"""
        mock_firestore_service.log_analytics_event.return_value = "doc_id_456"

        doc_id = analytics_logging_service.log_kg_node_click(
            course_id="course1",
            node_id="node1",
            node_label="Test Node",
            node_type="topic"
        )

        self.assertEqual(doc_id, "doc_id_456")
        
        call_args = mock_firestore_service.log_analytics_event.call_args[0][0]

        self.assertEqual(call_args['type'], 'kg_click')
        self.assertEqual(call_args['course_id'], 'course1')
        self.assertEqual(call_args['node_id'], 'node1')

if __name__ == '__main__':
    unittest.main()
