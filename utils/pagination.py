"""
Pagination utilities for handling large result sets
"""

from typing import Callable, Any, Optional, List, Dict


class PaginationIterator:
    """
    Generic pagination iterator for handling paginated API responses

    This class provides a reusable iterator pattern for paginating through
    API results with different endpoints and response formats.
    """

    def __init__(
        self,
        api_method: Callable,
        initial_params: Dict[str, Any],
        page_key: str = "lastFileID",
        items_key: str = "fileList",
        callback: Optional[Callable[[List[Any]], None]] = None,
    ):
        """
        Initialize PaginationIterator

        Args:
            api_method: The API method to call for each page (e.g., api.get_file_list)
            initial_params: Initial parameters to pass to the API method
            page_key: The key in the response that indicates the next page cursor
            items_key: The key in the response that contains the list of items
            callback: Optional callback function to process each page of items
        """
        self.api_method = api_method
        self.initial_params = initial_params.copy()
        self.page_key = page_key
        self.items_key = items_key
        self.callback = callback
        self.current_page = []
        self.current_index = 0
        self.is_exhausted = False
        self.total_items = 0

    def __iter__(self):
        """Initialize iterator"""
        self.current_page = []
        self.current_index = 0
        self.is_exhausted = False
        self.total_items = 0
        return self

    def __next__(self) -> Any:
        """Get next item from pagination"""
        # Fetch next page if current page is exhausted
        if self.current_index >= len(self.current_page):
            if self.is_exhausted:
                raise StopIteration

            # Fetch next page
            if not self._fetch_next_page():
                raise StopIteration

        # Return current item and advance index
        item = self.current_page[self.current_index]
        self.current_index += 1
        self.total_items += 1
        return item

    def _fetch_next_page(self) -> bool:
        """
        Fetch next page of results

        Returns:
            bool: True if more pages available, False otherwise
        """
        try:
            response = self.api_method(**self.initial_params)

            if response is None or (isinstance(response, tuple) and response[0] is None):
                return False

            # Handle tuple responses (for backward compatibility)
            if isinstance(response, tuple):
                items, next_cursor = response
            else:
                # Handle dict responses (for share list)
                items = response.get(self.items_key, [])
                next_cursor = response.get(self.page_key)

            self.current_page = items
            self.current_index = 0

            # Execute callback if provided
            if self.callback and items:
                self.callback(items)

            # Check if there are more pages
            if next_cursor is None or next_cursor == -1:
                self.is_exhausted = True
            else:
                # Update the cursor for next request
                # Determine the appropriate parameter name
                if "file" in self.page_key.lower():
                    self.initial_params["last_file_id"] = next_cursor
                elif "share" in self.page_key.lower():
                    self.initial_params["last_share_id"] = next_cursor
                else:
                    self.initial_params[self.page_key] = next_cursor

            return len(items) > 0

        except Exception as e:
            print(f"Error fetching page: {e}")
            return False

    def get_all(self) -> List[Any]:
        """
        Get all items from all pages

        Returns:
            List of all items from all pages
        """
        items = []
        for item in self:
            items.append(item)
        return items

    def get_total_items(self) -> int:
        """
        Get total number of items fetched so far

        Returns:
            Total number of items fetched
        """
        return self.total_items


class FileListPaginator(PaginationIterator):
    """Specialized paginator for file list pagination"""

    def __init__(
        self,
        api_method: Callable,
        parent_file_id: int = 0,
        limit: int = 100,
        callback: Optional[Callable[[List[Dict]], None]] = None,
    ):
        """
        Initialize FileListPaginator

        Args:
            api_method: The API method for getting file lists
            parent_file_id: Parent folder ID to list files from
            limit: Number of items per page
            callback: Optional callback for processing each page
        """
        initial_params = {
            "parent_file_id": parent_file_id,
            "limit": limit,
        }
        super().__init__(
            api_method=api_method,
            initial_params=initial_params,
            page_key="lastFileID",
            items_key="fileList",
            callback=callback,
        )

    def set_parent_folder(self, parent_file_id: int) -> None:
        """Change the parent folder for pagination"""
        self.initial_params["parent_file_id"] = parent_file_id


class ShareListPaginator(PaginationIterator):
    """Specialized paginator for share list pagination"""

    def __init__(
        self,
        api_method: Callable,
        limit: int = 100,
        callback: Optional[Callable[[List[Dict]], None]] = None,
    ):
        """
        Initialize ShareListPaginator

        Args:
            api_method: The API method for getting share lists
            limit: Number of items per page
            callback: Optional callback for processing each page
        """
        initial_params = {
            "limit": limit,
        }
        super().__init__(
            api_method=api_method,
            initial_params=initial_params,
            page_key="lastShareId",
            items_key="shareList",
            callback=callback,
        )
