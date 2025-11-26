"""
Configuration file for 123Pan API wrapper
Defines API endpoints, constants, and default settings
"""

# API Base Configuration
API_BASE_URL = "https://open-api.123pan.com/api"
PLATFORM_HEADER = "open_platform"
DEFAULT_TIMEOUT = 30  # seconds
TOKEN_FILE_PATH = "./access.json"

# API Endpoints
ENDPOINTS = {
    "access_token": f"{API_BASE_URL}/v1/access_token",
    "direct_link_enable": f"{API_BASE_URL}/v1/direct-link/enable",
    "direct_link_disable": f"{API_BASE_URL}/v1/direct-link/disable",
    "direct_link_get": f"{API_BASE_URL}/v1/direct-link/get",
    "file_list": f"{API_BASE_URL}/v2/file/list",
    "file_info": f"{API_BASE_URL}/v1/file/info",
    "file_move": f"{API_BASE_URL}/v1/file/move",
    "file_rename": f"{API_BASE_URL}/v1/file/rename",
    "file_trash": f"{API_BASE_URL}/v1/file/trash",
    "file_delete": f"{API_BASE_URL}/v1/file/delete",
    "file_recover": f"{API_BASE_URL}/v1/file/recover",
    "share_list": f"{API_BASE_URL}/v1/share/list",
    "share_update": f"{API_BASE_URL}/v1/share/update",
    "share_create": f"{API_BASE_URL}/v1/share/create",
}

# Default pagination settings
DEFAULT_PAGE_LIMIT = 100
MAX_PAGE_LIMIT = 100
MIN_PAGE_LIMIT = 1

# Token expiration settings
TOKEN_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TOKEN_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

# Default file ID (root directory)
ROOT_DIRECTORY_ID = 0

# API Response Codes
SUCCESS_CODE = 0

# File operation defaults
DEFAULT_PARENT_FILE_ID = 0

# Share settings
DEFAULT_SHARE_DOWNLOAD_COUNT = -1  # -1 means unlimited
DEFAULT_SHARE_DURATION = 2592000   # 30 days in seconds
