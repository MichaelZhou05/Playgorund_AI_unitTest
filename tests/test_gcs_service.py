import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import gcs_service

class TestGCSService(unittest.TestCase):
    """Test suite for GCS service functions"""

    @patch('app.services.gcs_service.storage.Client')
    def test_ensure_bucket_exists_already_exists(self, mock_client):
        """Test ensure_bucket_exists when the bucket already exists"""
        mock_bucket = MagicMock()
        mock_client.return_value.get_bucket.return_value = mock_bucket
        
        bucket = gcs_service.ensure_bucket_exists('test-bucket')

        self.assertEqual(bucket, mock_bucket)
        mock_client.return_value.get_bucket.assert_called_with('test-bucket')
        mock_client.return_value.create_bucket.assert_not_called()

    @patch('app.services.gcs_service.storage.Client')
    def test_ensure_bucket_exists_creates_new(self, mock_client):
        """Test ensure_bucket_exists when the bucket needs to be created"""
        mock_client.return_value.get_bucket.side_effect = Exception("Bucket not found")
        mock_bucket = MagicMock()
        mock_client.return_value.create_bucket.return_value = mock_bucket

        bucket = gcs_service.ensure_bucket_exists('new-bucket')

        self.assertEqual(bucket, mock_bucket)
        mock_client.return_value.get_bucket.assert_called_with('new-bucket')
        mock_client.return_value.create_bucket.assert_called_with('new-bucket', location='us-central1')

    @patch('app.services.gcs_service.ensure_bucket_exists')
    @patch('os.path.exists', return_value=True)
    def test_upload_course_files(self, mock_path_exists, mock_ensure_bucket):
        """Test upload_course_files function"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_ensure_bucket.return_value = mock_bucket

        files_to_upload = [{'id': '1', 'local_path': '/fake/path/file1.pdf', 'display_name': 'file1.pdf'}]
        
        updated_files = gcs_service.upload_course_files(files_to_upload, '123', 'test-bucket')

        mock_ensure_bucket.assert_called_with('test-bucket')
        mock_bucket.blob.assert_called_with('courses/123/file1.pdf')
        mock_blob.upload_from_filename.assert_called_with('/fake/path/file1.pdf')
        self.assertEqual(updated_files[0]['gcs_uri'], 'gs://test-bucket/courses/123/file1.pdf')

    @patch('app.services.gcs_service.get_storage_client')
    def test_generate_signed_url(self, mock_get_client):
        """Test generate_signed_url function"""
        mock_blob = MagicMock()
        mock_blob.generate_signed_url.return_value = 'http://signed-url'
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        gcs_uri = 'gs://test-bucket/path/to/file.pdf'
        url = gcs_service.generate_signed_url(gcs_uri)

        self.assertEqual(url, 'http://signed-url')
        mock_bucket.blob.assert_called_with('path/to/file.pdf')

if __name__ == '__main__':
    unittest.main()
