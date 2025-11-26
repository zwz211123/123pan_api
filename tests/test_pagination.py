"""
Tests for pagination utilities
"""

import unittest
from unittest.mock import Mock, patch
from utils.pagination import PaginationIterator


class TestPaginationIterator(unittest.TestCase):
    """Test cases for PaginationIterator"""

    def test_iterator_with_dict_response(self):
        """Test iterator with dict-based API response"""
        # Mock API that returns dict response
        responses = [
            {
                "shareList": [{"id": 1}, {"id": 2}],
                "lastShareId": 123
            },
            {
                "shareList": [{"id": 3}],
                "lastShareId": None
            }
        ]

        api_method = Mock(side_effect=responses)

        paginator = PaginationIterator(
            api_method=api_method,
            initial_params={"limit": 2},
            page_key="lastShareId",
            items_key="shareList"
        )

        items = list(paginator)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["id"], 1)
        self.assertEqual(items[2]["id"], 3)

    def test_iterator_with_tuple_response(self):
        """Test iterator with tuple-based API response"""
        # Mock API that returns tuple response
        responses = [
            ([{"id": 1}, {"id": 2}], 123),
            ([{"id": 3}], None)
        ]

        api_method = Mock(side_effect=responses)

        paginator = PaginationIterator(
            api_method=api_method,
            initial_params={"limit": 2},
            page_key="lastFileID",
            items_key="fileList"
        )

        items = list(paginator)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["id"], 1)
        self.assertEqual(items[2]["id"], 3)

    def test_iterator_with_callback(self):
        """Test iterator callback functionality"""
        callback = Mock()

        responses = [
            {
                "shareList": [{"id": 1}, {"id": 2}],
                "lastShareId": None
            }
        ]

        api_method = Mock(side_effect=responses)

        paginator = PaginationIterator(
            api_method=api_method,
            initial_params={"limit": 2},
            page_key="lastShareId",
            items_key="shareList",
            callback=callback
        )

        list(paginator)

        # Callback should be called with the items
        callback.assert_called_once()

    def test_get_all_method(self):
        """Test get_all method"""
        responses = [
            {
                "shareList": [{"id": 1}, {"id": 2}],
                "lastShareId": 123
            },
            {
                "shareList": [{"id": 3}],
                "lastShareId": None
            }
        ]

        api_method = Mock(side_effect=responses)

        paginator = PaginationIterator(
            api_method=api_method,
            initial_params={"limit": 2},
            page_key="lastShareId",
            items_key="shareList"
        )

        items = paginator.get_all()
        self.assertEqual(len(items), 3)

    def test_total_items_count(self):
        """Test total items count tracking"""
        responses = [
            {
                "shareList": [{"id": 1}, {"id": 2}],
                "lastShareId": 123
            },
            {
                "shareList": [{"id": 3}],
                "lastShareId": None
            }
        ]

        api_method = Mock(side_effect=responses)

        paginator = PaginationIterator(
            api_method=api_method,
            initial_params={"limit": 2},
            page_key="lastShareId",
            items_key="shareList"
        )

        list(paginator)
        self.assertEqual(paginator.get_total_items(), 3)

    def test_empty_response(self):
        """Test handling empty response"""
        api_method = Mock(return_value=None)

        paginator = PaginationIterator(
            api_method=api_method,
            initial_params={"limit": 2},
            page_key="lastShareId",
            items_key="shareList"
        )

        items = list(paginator)
        self.assertEqual(len(items), 0)

    def test_cursor_parameter_update(self):
        """Test that cursor parameters are updated correctly for next page"""
        responses = [
            {
                "shareList": [{"id": 1}],
                "lastShareId": 456
            },
            {
                "shareList": [{"id": 2}],
                "lastShareId": None
            }
        ]

        api_method = Mock(side_effect=responses)

        initial_params = {"limit": 1}
        paginator = PaginationIterator(
            api_method=api_method,
            initial_params=initial_params,
            page_key="lastShareId",
            items_key="shareList"
        )

        # Iterate through all items to trigger second page fetch
        items = list(paginator)

        # Check that the cursor was updated in paginator's internal params for the second page request
        self.assertEqual(len(items), 2)
        self.assertIn("last_share_id", paginator.initial_params)
        self.assertEqual(paginator.initial_params["last_share_id"], 456)


if __name__ == "__main__":
    unittest.main()
