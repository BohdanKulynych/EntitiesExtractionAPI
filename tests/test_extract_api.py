import unittest
import os
from io import BytesIO
from src.api import app


class TestEntityExtractionAPI(unittest.TestCase):

    def setUp(self):
        # Using flask test_client for testing
        self.app = app.test_client()
        self.app.testing = True
        self.test_files_dir = os.path.join(os.getcwd(), 'tests/test_data/')

    def test_no_file_in_request(self):
        response = self.app.post('/api/v1/extract')
        self.assertEqual(response.status_code, 400)
        self.assertIn("No file part", response.json['error'])

    def test_no_selected_file(self):
        data = {'file': (BytesIO(b''), '')}
        response = self.app.post('/api/v1/extract', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn("No selected file", response.json['error'])

    def test_unsupported_file_type(self):
        data = {'file': (BytesIO(b'test content'), 'test.txt')}
        response = self.app.post('/api/v1/extract', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 415)
        self.assertIn("Unsupported file type", response.json['error'])

    def test_valid_pdf_file(self):
        with open(os.path.join(self.test_files_dir, 'valid_pdf.pdf'), 'rb') as f:
            data = {'file': (f, 'valid_pdf.pdf')}
            response = self.app.post('/api/v1/extract', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertIn("clinical_entities", response.json)
        self.assertIn("drug_entities", response.json)

    def test_invalid_pdf_file(self):
        # Input data - word file with changed extension
        with open(os.path.join(self.test_files_dir, 'invalid_pdf.pdf'), 'rb') as f:
            data = {'file': (f, 'invalid_pdf.pdf')}
            response = self.app.post('/api/v1/extract', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 500)
        self.assertIn("Not a PDF file", response.json['error'])

    def test_empty_pdf_file(self):
        with open(os.path.join(self.test_files_dir, 'empty_pdf.pdf'), 'rb') as f:
            data = {'file': (f, 'empty_pdf.pdf')}
            response = self.app.post('/api/v1/extract', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 500)

    def test_file_size_limit(self):
        # Create a dummy file larger than the 5 MB limit
        large_file_content = BytesIO(b"A" * (5 * 1024 * 1024 + 1))
        large_file_content.name = 'large_test.pdf'

        response = self.app.post('/api/v1/extract', content_type='multipart/form-data', data={
            'file': (large_file_content, 'large_test.pdf')
        })

        self.assertEqual(response.status_code, 413)
        self.assertIn(b'File too large', response.data)
