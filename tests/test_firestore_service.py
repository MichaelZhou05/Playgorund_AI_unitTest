"""
Unit tests for firestore_service.py
Tests all Firestore operations with mocked Firebase client.
"""
import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the google.cloud.firestore module before importing firestore_service
mock_firestore_module = MagicMock()
mock_firestore_class = MagicMock()
mock_firestore_module.Client = mock_firestore_class
sys.modules['google.cloud.firestore'] = mock_firestore_module
sys.modules['google.cloud'] = MagicMock()

# Now we can import the service
from app.services import firestore_service


class TestFirestoreService(unittest.TestCase):
    """Test suite for Firestore service functions"""
    
    def setUp(self):
        """Set up test fixtures before each test"""
        # Create a fresh mock db for each test
        self.mock_db = MagicMock()
        
        # Replace the service's db with our mock
        firestore_service.db = self.mock_db
        self.service = firestore_service
    
    
    # ==================== TEST get_course_state ====================
    
    def test_get_course_state_needs_init(self):
        """Test get_course_state when course document doesn't exist"""
        # Mock document that doesn't exist
        mock_doc = Mock()
        mock_doc.exists = False
        
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = self.service.get_course_state('course_123')
        
        self.assertEqual(result, 'NEEDS_INIT')
        self.mock_db.collection.assert_called_with('courses')
        self.mock_db.collection.return_value.document.assert_called_with('course_123')
    
    def test_get_course_state_generating(self):
        """Test get_course_state when course is in GENERATING state"""
        # Mock document with GENERATING status
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.get.return_value = 'GENERATING'
        
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = self.service.get_course_state('course_456')
        
        self.assertEqual(result, 'GENERATING')
    
    def test_get_course_state_active(self):
        """Test get_course_state when course is ACTIVE"""
        # Mock document with ACTIVE status
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.get.return_value = 'ACTIVE'
        
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = self.service.get_course_state('course_789')
        
        self.assertEqual(result, 'ACTIVE')
    
    def test_get_course_state_not_ready(self):
        """Test get_course_state when course has unknown status"""
        # Mock document with unknown status
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.get.return_value = 'UNKNOWN_STATUS'
        
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = self.service.get_course_state('course_999')
        
        self.assertEqual(result, 'NOT_READY')
    
    
    # ==================== TEST create_course_doc ====================
    
    def test_create_course_doc(self):
        """Test create_course_doc creates document with GENERATING status"""
        mock_set = Mock()
        self.mock_db.collection.return_value.document.return_value.set = mock_set
        
        self.service.create_course_doc('course_new')
        
        # Verify correct collection and document were called
        self.mock_db.collection.assert_called_with('courses')
        self.mock_db.collection.return_value.document.assert_called_with('course_new')
        
        # Verify set was called with correct data
        mock_set.assert_called_once_with({'status': 'GENERATING'})
    
    def test_create_course_doc_different_id(self):
        """Test create_course_doc with different course ID"""
        mock_set = Mock()
        self.mock_db.collection.return_value.document.return_value.set = mock_set
        
        self.service.create_course_doc('different_course_123')
        
        self.mock_db.collection.return_value.document.assert_called_with('different_course_123')
        mock_set.assert_called_once_with({'status': 'GENERATING'})
    
    
    # ==================== TEST get_course_data ====================
    
    def test_get_course_data_returns_document(self):
        """Test get_course_data returns the DocumentSnapshot"""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = 'course_123'
        
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = self.service.get_course_data('course_123')
        
        self.assertEqual(result, mock_doc)
        self.mock_db.collection.assert_called_with('courses')
        self.mock_db.collection.return_value.document.assert_called_with('course_123')
    
    def test_get_course_data_nonexistent_course(self):
        """Test get_course_data for nonexistent course"""
        mock_doc = Mock()
        mock_doc.exists = False
        
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        result = self.service.get_course_data('nonexistent_course')
        
        self.assertFalse(result.exists)
    
    
    # ==================== TEST finalize_course_doc ====================
    
    def test_finalize_course_doc_complete_data(self):
        """Test finalize_course_doc with all data fields"""
        mock_update = Mock()
        self.mock_db.collection.return_value.document.return_value.update = mock_update
        
        test_data = {
            'corpus_id': 'corpus_abc123',
            'indexed_files': ['file1.pdf', 'file2.pdf'],
            'kg_nodes': '[{"id": "node1"}]',
            'kg_edges': '[{"from": "node1", "to": "node2"}]',
            'kg_data': '{"topic_1": {"summary": "..."}}'
        }
        
        self.service.finalize_course_doc('course_final', test_data)
        
        # Verify correct collection and document
        self.mock_db.collection.assert_called_with('courses')
        self.mock_db.collection.return_value.document.assert_called_with('course_final')
        
        # Verify update was called with correct data
        expected_update = {
            'status': 'ACTIVE',
            'corpus_id': 'corpus_abc123',
            'indexed_files': ['file1.pdf', 'file2.pdf'],
            'kg_nodes': '[{"id": "node1"}]',
            'kg_edges': '[{"from": "node1", "to": "node2"}]',
            'kg_data': '{"topic_1": {"summary": "..."}}'
        }
        mock_update.assert_called_once_with(expected_update)
    
    def test_finalize_course_doc_partial_data(self):
        """Test finalize_course_doc with missing optional fields"""
        mock_update = Mock()
        self.mock_db.collection.return_value.document.return_value.update = mock_update
        
        test_data = {
            'corpus_id': 'corpus_xyz',
            # Missing other fields
        }
        
        self.service.finalize_course_doc('course_partial', test_data)
        
        # Verify update includes None for missing fields
        expected_update = {
            'status': 'ACTIVE',
            'corpus_id': 'corpus_xyz',
            'indexed_files': None,
            'kg_nodes': None,
            'kg_edges': None,
            'kg_data': None
        }
        mock_update.assert_called_once_with(expected_update)
    
    def test_finalize_course_doc_empty_data(self):
        """Test finalize_course_doc with empty data dictionary"""
        mock_update = Mock()
        self.mock_db.collection.return_value.document.return_value.update = mock_update
        
        self.service.finalize_course_doc('course_empty', {})
        
        # Verify update sets status to ACTIVE with None for all fields
        expected_update = {
            'status': 'ACTIVE',
            'corpus_id': None,
            'indexed_files': None,
            'kg_nodes': None,
            'kg_edges': None,
            'kg_data': None
        }
        mock_update.assert_called_once_with(expected_update)
    
    
    # ==================== INTEGRATION TESTS ====================
    
    def test_full_course_lifecycle(self):
        """Test the complete course lifecycle: create -> check state -> finalize"""
        # Step 1: Create course
        mock_set = Mock()
        self.mock_db.collection.return_value.document.return_value.set = mock_set
        self.service.create_course_doc('course_lifecycle')
        mock_set.assert_called_once()
        
        # Step 2: Check state (should be GENERATING)
        mock_doc_generating = Mock()
        mock_doc_generating.exists = True
        mock_doc_generating.get.return_value = 'GENERATING'
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc_generating
        
        state = self.service.get_course_state('course_lifecycle')
        self.assertEqual(state, 'GENERATING')
        
        # Step 3: Finalize course
        mock_update = Mock()
        self.mock_db.collection.return_value.document.return_value.update = mock_update
        
        final_data = {
            'corpus_id': 'corpus_final',
            'indexed_files': ['file.pdf'],
            'kg_nodes': '[]',
            'kg_edges': '[]',
            'kg_data': '{}'
        }
        self.service.finalize_course_doc('course_lifecycle', final_data)
        mock_update.assert_called_once()
        
        # Step 4: Check state (should be ACTIVE)
        mock_doc_active = Mock()
        mock_doc_active.exists = True
        mock_doc_active.get.return_value = 'ACTIVE'
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc_active
        
        state = self.service.get_course_state('course_lifecycle')
        self.assertEqual(state, 'ACTIVE')


if __name__ == '__main__':
    unittest.main()

