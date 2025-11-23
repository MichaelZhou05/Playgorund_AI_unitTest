import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import numpy as np

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import analytics_reporting_service

class TestAnalyticsReportingService(unittest.TestCase):
    """Test suite for Analytics Reporting service functions"""

    @patch('app.services.analytics_reporting_service.firestore_service')
    @patch('app.services.analytics_reporting_service.gemini_service')
    @patch('app.services.analytics_reporting_service._perform_clustering')
    def test_run_daily_analytics(self, mock_perform_clustering, mock_gemini_service, mock_firestore_service):
        """Test the main run_daily_analytics function"""
        # Mock the data returned from Firestore
        mock_events = [
            {'doc_id': '1', 'query_text': 'What is a test?', 'query_vector': [0.1, 0.2, 0.3]},
            {'doc_id': '2', 'query_text': 'How does this work?', 'query_vector': [0.4, 0.5, 0.6]},
            {'doc_id': '3', 'query_text': 'Another question', 'query_vector': [0.7, 0.8, 0.9]},
            {'doc_id': '4', 'query_text': 'More testing', 'query_vector': [0.1, 0.2, 0.3]},
            {'doc_id': '5', 'query_text': 'Final test', 'query_vector': [0.4, 0.5, 0.6]},
        ]
        mock_firestore_service.get_analytics_events.return_value = mock_events
        mock_firestore_service.get_analytics_events_by_ids.return_value = mock_events

        # Mock the clustering results
        mock_perform_clustering.return_value = (np.array([0, 1, 0, 0, 1]), np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]))

        # Mock the AI labeling
        mock_gemini_service.generate_answer.side_effect = ["Test Questions", "General Questions"]

        report = analytics_reporting_service.run_daily_analytics("course1", n_clusters=2, auto_detect_clusters=False)

        # Assertions
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(report['total_queries'], 5)
        self.assertEqual(report['num_clusters'], 2)
        self.assertIn("Test Questions", report['clusters'])
        self.assertIn("General Questions", report['clusters'])
        self.assertEqual(report['clusters']['Test Questions']['count'], 3)
        self.assertEqual(report['clusters']['General Questions']['count'], 2)
        mock_firestore_service.save_analytics_report.assert_called_once()


    def test_extract_vectors(self):
        """Test the _extract_vectors helper function"""
        events = [
            {'doc_id': '1', 'query_vector': [0.1, 0.2]},
            {'doc_id': '2'}, # No vector
            {'doc_id': '3', 'query_vector': [0.3, 0.4]},
        ]
        vectors, doc_ids = analytics_reporting_service._extract_vectors(events)

        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(doc_ids), 2)
        self.assertEqual(doc_ids[0], '1')
        self.assertEqual(doc_ids[1], '3')

if __name__ == '__main__':
    unittest.main()
