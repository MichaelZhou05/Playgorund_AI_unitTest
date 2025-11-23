import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import kg_service

class TestKgService(unittest.TestCase):
    """Test suite for KG service functions"""

    def setUp(self):
        self.sample_files = [
            {'id': '101', 'name': 'Chapter 3.pdf', 'display_name': 'Chapter 3.pdf'},
            {'id': '102', 'name': 'Lecture 5.pdf', 'display_name': 'Lecture 5.pdf'},
        ]
        self.sample_topics = ['Cell Mitosis', 'DNA Replication']
        self.corpus_id = 'corpus_id_123'

    @patch('app.services.kg_service.gemini_service.generate_answer_with_context')
    def test_build_knowledge_graph(self, mock_generate_answer):
        """Test the main build_knowledge_graph function"""
        # Mock the return value of the gemini service
        mock_generate_answer.return_value = ("This is a summary", [{'filename': 'Chapter 3.pdf'}])

        nodes_json, edges_json, data_json = kg_service.build_knowledge_graph(
            self.sample_topics, self.corpus_id, self.sample_files
        )

        nodes = json.loads(nodes_json)
        edges = json.loads(edges_json)
        data = json.loads(data_json)

        self.assertEqual(len(nodes), 4) # 2 topics + 2 files
        self.assertEqual(len(edges), 2) # 2 topics, each connected to one file
        self.assertIn('topic_1', data)
        self.assertIn('topic_2', data)
        self.assertEqual(data['topic_1']['summary'], "This is a summary")

    @patch('app.services.kg_service.gemini_service.generate_answer')
    def test_extract_topics_from_summaries(self, mock_generate_answer):
        """Test extract_topics_from_summaries function"""
        mock_generate_answer.return_value = "Topic 1, Topic 2, Topic 3"

        topics = kg_service.extract_topics_from_summaries(["summary 1", "summary 2"])

        self.assertEqual(len(topics), 3)
        self.assertEqual(topics[0], "Topic 1")

    @patch('app.services.kg_service.gemini_service.generate_answer_with_context')
    def test_add_topic_to_graph(self, mock_generate_answer):
        """Test add_topic_to_graph function"""
        mock_generate_answer.return_value = ("New summary", [{'filename': 'Lecture 5.pdf'}])

        existing_nodes = [
            {'id': 'topic_1', 'label': 'Old Topic', 'group': 'topic'},
            {'id': '102', 'label': 'Lecture 5.pdf', 'group': 'file_pdf'}
        ]
        existing_edges = []
        existing_data = {'topic_1': {'summary': 'Old summary', 'sources': []}}

        nodes_json, edges_json, data_json = kg_service.add_topic_to_graph(
            "New Topic", self.corpus_id, existing_nodes, existing_edges, existing_data
        )

        nodes = json.loads(nodes_json)
        edges = json.loads(edges_json)
        data = json.loads(data_json)

        self.assertEqual(len(nodes), 3) # 1 old topic + 1 file + 1 new topic
        self.assertEqual(len(edges), 1) # new topic connected to file
        self.assertIn('topic_2', data)
        self.assertEqual(data['topic_2']['summary'], "New summary")

    def test_remove_topic_from_graph(self):
        """Test remove_topic_from_graph function"""
        existing_nodes = [
            {'id': 'topic_1', 'label': 'Topic to Remove', 'group': 'topic'},
            {'id': 'topic_2', 'label': 'Another Topic', 'group': 'topic'},
            {'id': '101', 'label': 'File.pdf', 'group': 'file_pdf'}
        ]
        existing_edges = [
            {'from': 'topic_1', 'to': '101'},
            {'from': 'topic_2', 'to': '101'}
        ]
        existing_data = {
            'topic_1': {'summary': 'summary 1'},
            'topic_2': {'summary': 'summary 2'}
        }

        nodes_json, edges_json, data_json = kg_service.remove_topic_from_graph(
            'topic_1', existing_nodes, existing_edges, existing_data
        )
        
        nodes = json.loads(nodes_json)
        edges = json.loads(edges_json)
        data = json.loads(data_json)

        self.assertEqual(len(nodes), 2) # topic_2 and the file
        self.assertEqual(len(edges), 1) # only the edge from topic_2
        self.assertNotIn('topic_1', data)
        self.assertIn('topic_2', data)


if __name__ == '__main__':
    unittest.main()
