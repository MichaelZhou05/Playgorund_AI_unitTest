import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import canvas_service

class TestCanvasService(unittest.TestCase):
    """Test suite for Canvas service functions"""

    @patch('app.services.canvas_service.requests.get')
    def test_get_course_files_single_page(self, mock_get):
        """Test get_course_files with a single page of results"""
        # Mock the requests.get call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 1, 'display_name': 'file1.pdf'},
            {'id': 2, 'display_name': 'file2.txt'},
            {'id': 3, 'display_name': 'file3.zip'}, # this should be filtered out
        ]
        mock_response.headers = {'Link': ''}
        mock_get.return_value = mock_response

        files, indexed_files = canvas_service.get_course_files('123', 'fake_token', download=False)

        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['display_name'], 'file1.pdf')
        self.assertEqual(files[1]['display_name'], 'file2.txt')
        self.assertIn('1', indexed_files)
        self.assertIn('2', indexed_files)
        self.assertNotIn('3', indexed_files)

    @patch('app.services.canvas_service.requests.get')
    def test_get_course_files_multiple_pages(self, mock_get):
        """Test get_course_files with pagination"""
        # Mock the requests.get calls for two pages
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [{'id': 1, 'display_name': 'file1.pdf'}]
        mock_response1.headers = {'Link': '<http://next-page>; rel="next"'}

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = [{'id': 2, 'display_name': 'file2.docx'}]
        mock_response2.headers = {'Link': ''}

        mock_get.side_effect = [mock_response1, mock_response2]

        files, _ = canvas_service.get_course_files('123', 'fake_token', download=False)

        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['display_name'], 'file1.pdf')
        self.assertEqual(files[1]['display_name'], 'file2.docx')

    @patch('app.services.canvas_service.requests.get')
    @patch('app.services.canvas_service.os.makedirs')
    @patch('builtins.open')
    def test_download_files(self, mock_open, mock_makedirs, mock_get):
        """Test the _download_files helper function"""
        # Mock the requests.get call for downloading a file
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'file content'
        mock_get.return_value = mock_response

        files_to_download = [{'id': '1', 'display_name': 'file1.pdf', 'url': 'http://download-url'}]
        canvas_service._download_files(files_to_download, 'fake_token', '123')

        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_get.assert_called_once_with('http://download-url', headers={'Authorization': 'Bearer fake_token'}, timeout=60)


    @patch('app.services.canvas_service.requests.get')
    def test_get_syllabus(self, mock_get):
        """Test get_syllabus function"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'syllabus_body': 'This is the syllabus'}
        mock_get.return_value = mock_response

        syllabus = canvas_service.get_syllabus('123', 'fake_token')

        self.assertEqual(syllabus, 'This is the syllabus')

    @patch('app.services.canvas_service.requests.get')
    def test_get_course_info(self, mock_get):
        """Test get_course_info function"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123',
            'name': 'Test Course',
            'course_code': 'TEST101'
        }
        mock_get.return_value = mock_response

        course_info = canvas_service.get_course_info('123', 'fake_token')

        self.assertEqual(course_info['name'], 'Test Course')
        self.assertEqual(course_info['course_code'], 'TEST101')

if __name__ == '__main__':
    unittest.main()
