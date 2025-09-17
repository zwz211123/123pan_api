# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python client for the 123Pan cloud storage API. The project provides both a programmatic API interface and an interactive command-line interface for managing files, shares, and direct links on 123Pan.

## Architecture

### Core Components

1. **`api.py`** - The main API client class (`PanAPI`)
   - Handles all HTTP requests to 123Pan API endpoints
   - Manages OAuth2 token lifecycle (automatic refresh)
   - Provides methods for file operations, sharing, and direct links
   - Stores credentials in `access.json` with automatic token management

2. **`main.py`** - Interactive CLI application
   - Menu-driven interface with three main sections: file management, sharing, direct links
   - Handles user input validation and error display
   - Delegates all API calls to the `PanAPI` class

3. **`needPageTurning.py`** - Pagination helper module
   - Implements recursive pagination for share list retrieval
   - Creates a global `api` instance for use in pagination functions

### Authentication Flow

The project uses OAuth2 with automatic token management:
1. Client credentials (`client_id`, `client_secret`) are stored in `access.json`
2. Access tokens are automatically obtained and refreshed (30-day expiry)
3. The `ensure_token()` method handles token validation and renewal
4. All API methods automatically ensure valid tokens before requests

### API Method Categories

- **Authentication**: `get_access_token()`, `ensure_token()`
- **File Management**: `get_file_list()`, `get_file_detail()`, `move_files()`, `rename_files()`, `trash_files()`, `delete_files()`, `recover_files()`
- **Direct Links**: `enable_direct_link()`, `disable_direct_link()`, `get_direct_link()`
- **Sharing**: `get_share_list()`, `create_share_link()`, `update_share_info()`

## Development Commands

### Testing the Application
```bash
python main.py
```

### Syntax Checking
```bash
python -m py_compile main.py api.py needPageTurning.py
```

### Direct API Usage
```python
from api import PanAPI
api = PanAPI(token_file="access.json")
access_token = api.ensure_token()
files, last_id = api.get_file_list(parent_file_id=0, limit=100)
```

## Configuration

### Initial Setup
Create `access.json` with your 123Pan application credentials:
```json
{
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "access_token": "",
    "expired_at": ""
}
```

The `access_token` and `expired_at` fields are automatically managed by the application.

## Error Handling Patterns

- API methods return `False` or `None` on failure and print error messages
- User input validation is implemented inconsistently (some functions have try/catch for `ValueError`, others don't)
- Network errors are caught as generic `Exception` and printed to console
- The main menu loops continue on invalid input rather than exiting

## Known Issues

- `api.py:85` uses bare `except:` clause
- Some input validation missing in `main.py:172` and `main.py:179`
- Input validation missing in `needPageTurning.py:6`
- Logical error in `needPageTurning.py:20` with `or` operator usage