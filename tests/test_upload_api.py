import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from api import PanAPI


class UploadAPITest(unittest.TestCase):
    def make_api(self):
        api = PanAPI.__new__(PanAPI)
        api.ensure_token = Mock(return_value="test-token")
        return api

    @patch("api.pan_api.requests.get")
    def test_get_upload_domains_uses_timeout_and_parses_response(self, mock_get):
        response = Mock(status_code=200)
        response.json.return_value = {
            "code": 0,
            "data": {"data": ["https://upload.example.com"]},
        }
        mock_get.return_value = response

        domains = self.make_api().get_upload_domains()

        self.assertEqual(domains, ["https://upload.example.com"])
        self.assertEqual(mock_get.call_args.kwargs["timeout"], 30)

    @patch("api.pan_api.requests.post")
    def test_upload_file_streams_file_and_uses_consistent_auth(self, mock_post):
        response = Mock(status_code=200)
        response.json.return_value = {
            "code": 0,
            "data": {"completed": True, "fileID": 123},
        }
        mock_post.return_value = response

        api = self.make_api()
        api.get_upload_domains = Mock(return_value=["upload.example.com/"])

        file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as file_obj:
                file_obj.write(b"upload test")
                file_path = file_obj.name

            self.assertEqual(api.upload_file(file_path, 9), 123)
        finally:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)

        self.assertEqual(
            mock_post.call_args.args[0],
            "https://upload.example.com/upload/v2/file/single/create",
        )
        kwargs = mock_post.call_args.kwargs
        self.assertEqual(kwargs["headers"]["Authorization"], "test-token")
        self.assertNotIsInstance(kwargs["files"]["file"][1], bytes)
        self.assertEqual(kwargs["timeout"], (10, 120))


if __name__ == "__main__":
    unittest.main()
