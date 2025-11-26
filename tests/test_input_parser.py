"""
Tests for CLI input parsing module
"""

import unittest
from cli.input_parser import InputParser


class TestInputParser(unittest.TestCase):
    """Test cases for InputParser class"""

    def test_parse_file_ids_valid(self):
        """Test parsing valid file IDs"""
        result = InputParser.parse_file_ids("1,2,3,4,5")
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_parse_file_ids_with_spaces(self):
        """Test parsing file IDs with spaces"""
        result = InputParser.parse_file_ids("1, 2, 3")
        self.assertEqual(result, [1, 2, 3])

    def test_parse_file_ids_invalid(self):
        """Test parsing invalid file IDs"""
        result = InputParser.parse_file_ids("1,a,3")
        self.assertIsNone(result)

    def test_parse_file_ids_empty(self):
        """Test parsing empty input"""
        result = InputParser.parse_file_ids("")
        self.assertIsNone(result)

    def test_parse_positive_int_valid(self):
        """Test parsing valid positive integer"""
        result = InputParser.parse_positive_int("42")
        self.assertEqual(result, 42)

    def test_parse_positive_int_zero(self):
        """Test parsing zero (not positive)"""
        result = InputParser.parse_positive_int("0")
        self.assertIsNone(result)

    def test_parse_positive_int_negative(self):
        """Test parsing negative integer"""
        result = InputParser.parse_positive_int("-5")
        self.assertIsNone(result)

    def test_parse_positive_int_invalid(self):
        """Test parsing non-numeric input"""
        result = InputParser.parse_positive_int("abc")
        self.assertIsNone(result)

    def test_parse_optional_int_valid(self):
        """Test parsing valid optional integer"""
        result = InputParser.parse_optional_int("100")
        self.assertEqual(result, 100)

    def test_parse_optional_int_empty_with_default(self):
        """Test parsing empty input with default"""
        result = InputParser.parse_optional_int("", default=50)
        self.assertEqual(result, 50)

    def test_parse_optional_string_valid(self):
        """Test parsing valid optional string"""
        result = InputParser.parse_optional_string("test string")
        self.assertEqual(result, "test string")

    def test_parse_optional_string_empty_with_default(self):
        """Test parsing empty string with default"""
        result = InputParser.parse_optional_string("", default="default")
        self.assertEqual(result, "default")

    def test_parse_choice_valid(self):
        """Test parsing valid choice"""
        result = InputParser.parse_choice("1", ["0", "1", "2", "3"])
        self.assertEqual(result, "1")

    def test_parse_choice_invalid(self):
        """Test parsing invalid choice"""
        result = InputParser.parse_choice("5", ["0", "1", "2", "3"])
        self.assertIsNone(result)

    def test_parse_non_negative_int_zero(self):
        """Test parsing zero as non-negative"""
        result = InputParser.parse_non_negative_int("0")
        self.assertEqual(result, 0)

    def test_parse_non_negative_int_positive(self):
        """Test parsing positive as non-negative"""
        result = InputParser.parse_non_negative_int("42")
        self.assertEqual(result, 42)

    def test_parse_non_negative_int_negative(self):
        """Test parsing negative as non-negative"""
        result = InputParser.parse_non_negative_int("-5")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
