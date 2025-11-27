"""
Input parsing and validation utilities for CLI
"""

from typing import Optional, List


class InputParser:
    """Handles parsing and validation of user input"""

    @staticmethod
    def parse_file_ids(input_str: str, separator: str = ",") -> Optional[List[int]]:
        """
        Parse file ID list from input string

        Args:
            input_str: Input string with file IDs
            separator: Separator between IDs (default: comma)

        Returns:
            List of integers, or None if parsing fails
        """
        if not input_str or not input_str.strip():
            return None

        try:
            ids = [int(id_str.strip()) for id_str in input_str.split(separator)]
            return ids
        except ValueError:
            return None

    @staticmethod
    def parse_share_ids(input_str: str, separator: str = ",") -> Optional[List[int]]:
        """
        Parse share ID list from input string

        Args:
            input_str: Input string with share IDs
            separator: Separator between IDs (default: comma)

        Returns:
            List of integers, or None if parsing fails
        """
        return InputParser.parse_file_ids(input_str, separator)

    @staticmethod
    def parse_positive_int(input_str: str, default: Optional[int] = None) -> Optional[int]:
        """
        Parse positive integer from input string

        Args:
            input_str: Input string
            default: Default value if input is empty

        Returns:
            Positive integer, or None if parsing fails
        """
        if not input_str or not input_str.strip():
            return default

        try:
            value = int(input_str.strip())
            if value > 0:
                return value
            return None
        except ValueError:
            return None

    @staticmethod
    def parse_non_negative_int(input_str: str, default: Optional[int] = None) -> Optional[int]:
        """
        Parse non-negative integer from input string

        Args:
            input_str: Input string
            default: Default value if input is empty

        Returns:
            Non-negative integer, or None if parsing fails
        """
        if not input_str or not input_str.strip():
            return default

        try:
            value = int(input_str.strip())
            if value >= 0:
                return value
            return None
        except ValueError:
            return None

    @staticmethod
    def parse_optional_int(input_str: str, default: Optional[int] = None) -> Optional[int]:
        """
        Parse optional integer from input string

        Args:
            input_str: Input string
            default: Default value if input is empty

        Returns:
            Integer or default value
        """
        if not input_str or not input_str.strip():
            return default

        try:
            return int(input_str.strip())
        except ValueError:
            return None

    @staticmethod
    def parse_optional_string(input_str: str, default: Optional[str] = None) -> Optional[str]:
        """
        Parse optional string from input

        Args:
            input_str: Input string
            default: Default value if input is empty

        Returns:
            String or default value
        """
        if not input_str or not input_str.strip():
            return default
        return input_str.strip()

    @staticmethod
    def parse_choice(input_str: str, valid_choices: List[str]) -> Optional[str]:
        """
        Parse and validate user choice from menu

        Args:
            input_str: Input string
            valid_choices: List of valid choices

        Returns:
            Valid choice, or None if invalid
        """
        choice = input_str.strip()
        if choice in valid_choices:
            return choice
        return None

    @staticmethod
    def prompt_file_ids(prompt: str = "请输入文件ID列表 (以逗号分隔): ") -> Optional[List[int]]:
        """
        Prompt user for file IDs and parse input

        Args:
            prompt: Prompt message

        Returns:
            List of file IDs or None if parsing fails
        """
        while True:
            input_str = input(prompt)
            ids = InputParser.parse_file_ids(input_str)
            if ids is not None:
                return ids
            print("输入无效，请输入正确的ID列表（用逗号分隔的数字）")

    @staticmethod
    def prompt_positive_int(
        prompt: str = "请输入数字: ",
        min_val: int = 1,
        max_val: Optional[int] = None
    ) -> int:
        """
        Prompt user for positive integer with optional range validation

        Args:
            prompt: Prompt message
            min_val: Minimum allowed value (default: 1)
            max_val: Maximum allowed value (optional)

        Returns:
            Positive integer within the specified range
        """
        while True:
            input_str = input(prompt)
            value = InputParser.parse_positive_int(input_str)
            if value is not None:
                if value < min_val:
                    print(f"输入无效，请输入不少于 {min_val} 的正整数")
                    continue
                if max_val and value > max_val:
                    print(f"输入无效，请输入 {min_val} 到 {max_val} 之间的数字")
                    continue
                return value
            print("输入无效，请输入正整数")

    @staticmethod
    def prompt_optional_int(
        prompt: str = "请输入数字 (可选): ",
        default: Optional[int] = None
    ) -> Optional[int]:
        """
        Prompt user for optional integer

        Args:
            prompt: Prompt message
            default: Default value if input is empty

        Returns:
            Integer or default value
        """
        input_str = input(prompt)
        return InputParser.parse_optional_int(input_str, default)

    @staticmethod
    def prompt_optional_string(
        prompt: str = "请输入文本 (可选): ",
        default: Optional[str] = None
    ) -> Optional[str]:
        """
        Prompt user for optional string

        Args:
            prompt: Prompt message
            default: Default value if input is empty

        Returns:
            String or default value
        """
        input_str = input(prompt)
        return InputParser.parse_optional_string(input_str, default)
