"""
Custom exceptions for 123Pan API wrapper
"""


class PanAPIException(Exception):
    """Base exception for all 123Pan API errors"""

    def __init__(self, message, code=None, original_error=None):
        """
        Initialize PanAPIException

        Args:
            message: Error message
            code: API error code (if applicable)
            original_error: Original exception (if wrapped)
        """
        self.message = message
        self.code = code
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class TokenExpiredError(PanAPIException):
    """Raised when access token has expired or is invalid"""

    def __init__(self, message="Access token has expired or is invalid"):
        super().__init__(message, code="TOKEN_EXPIRED")


class TokenNotFoundError(PanAPIException):
    """Raised when access token file is not found"""

    def __init__(self, message="Access token file not found"):
        super().__init__(message, code="TOKEN_NOT_FOUND")


class APIError(PanAPIException):
    """Raised when API request fails"""

    def __init__(self, message, code=None, status_code=None, response_data=None):
        """
        Initialize APIError

        Args:
            message: Error message
            code: API error code
            status_code: HTTP status code
            response_data: Full API response data
        """
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message, code=code)

    def __str__(self):
        result = super().__str__()
        if self.status_code:
            result += f" (HTTP {self.status_code})"
        return result


class NetworkError(PanAPIException):
    """Raised when network request fails"""

    def __init__(self, message, original_error=None):
        """
        Initialize NetworkError

        Args:
            message: Error message
            original_error: Original exception from requests library
        """
        super().__init__(message, code="NETWORK_ERROR", original_error=original_error)


class InvalidParameterError(PanAPIException):
    """Raised when invalid parameters are provided"""

    def __init__(self, parameter_name, message="Invalid parameter"):
        """
        Initialize InvalidParameterError

        Args:
            parameter_name: Name of the invalid parameter
            message: Detailed error message
        """
        full_message = f"{parameter_name}: {message}"
        super().__init__(full_message, code="INVALID_PARAMETER")


class CredentialsError(PanAPIException):
    """Raised when credentials are missing or invalid"""

    def __init__(self, message="Client credentials are missing or invalid"):
        super().__init__(message, code="CREDENTIALS_ERROR")


class FileNotFoundError(PanAPIException):
    """Raised when requested file is not found"""

    def __init__(self, file_id=None, message="File not found"):
        if file_id:
            message = f"File (ID: {file_id}) not found"
        super().__init__(message, code="FILE_NOT_FOUND")
