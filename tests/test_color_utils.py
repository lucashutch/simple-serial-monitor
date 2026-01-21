"""Test color utility functionality."""

import pytest
from src.embedded_cereal_bowl.utils.color_utils import colour_str
from colorama import Fore, Back, Style


class TestColourStr:
    """Test cases for the colour_str class."""

    def test_initialization(self):
        """Test colour_str initialization."""
        cs = colour_str("test")
        assert cs.s == "test"
        assert cs.codes == []

    def test_no_colors_string_conversion(self):
        """Test string conversion without any colors."""
        cs = colour_str("test")
        result = str(cs)
        assert result == "test"

    def test_single_color_red(self):
        """Test single color application (red)."""
        cs = colour_str("test")
        result = str(cs.red())
        expected = f"{Fore.RED}test{Style.RESET_ALL}"
        assert result == expected

    def test_single_color_green(self):
        """Test single color application (green)."""
        cs = colour_str("test")
        result = str(cs.green())
        expected = f"{Fore.GREEN}test{Style.RESET_ALL}"
        assert result == expected

    def test_single_color_yellow(self):
        """Test single color application (yellow)."""
        cs = colour_str("test")
        result = str(cs.yellow())
        expected = f"{Fore.YELLOW}test{Style.RESET_ALL}"
        assert result == expected

    def test_single_color_blue(self):
        """Test single color application (blue)."""
        cs = colour_str("test")
        result = str(cs.blue())
        expected = f"{Fore.BLUE}test{Style.RESET_ALL}"
        assert result == expected

    def test_single_color_black(self):
        """Test single color application (black)."""
        cs = colour_str("test")
        result = str(cs.black())
        expected = f"{Fore.BLACK}test{Style.RESET_ALL}"
        assert result == expected

    def test_background_colors(self):
        """Test background color application."""
        # Test each color on a fresh colour_str instance
        cs_red = colour_str("test")
        result = str(cs_red.back_red())
        expected = f"{Back.RED}test{Style.RESET_ALL}"
        assert result == expected

        cs_green = colour_str("test")
        result = str(cs_green.back_green())
        expected = f"{Back.GREEN}test{Style.RESET_ALL}"
        assert result == expected

        cs_blue = colour_str("test")
        result = str(cs_blue.back_blue())
        expected = f"{Back.BLUE}test{Style.RESET_ALL}"
        assert result == expected

        cs_yellow = colour_str("test")
        result = str(cs_yellow.back_yellow())
        expected = f"{Back.YELLOW}test{Style.RESET_ALL}"
        assert result == expected

    def test_style_modifiers(self):
        """Test style modifier application."""
        cs_dim = colour_str("test")
        result = str(cs_dim.dim())
        expected = f"{Style.DIM}test{Style.RESET_ALL}"
        assert result == expected

        cs_bright = colour_str("test")
        result = str(cs_bright.bright())
        expected = f"{Style.BRIGHT}test{Style.RESET_ALL}"
        assert result == expected

    def test_color_chaining(self):
        """Test chaining multiple colors."""
        cs = colour_str("test")
        result = str(cs.red().bright())
        expected = f"{Fore.RED}{Style.BRIGHT}test{Style.RESET_ALL}"
        assert result == expected

    def test_complex_chaining(self):
        """Test complex chaining with multiple styles."""
        cs = colour_str("test")
        result = str(cs.green().bright().back_yellow())
        expected = f"{Fore.GREEN}{Style.BRIGHT}{Back.YELLOW}test{Style.RESET_ALL}"
        assert result == expected

    def test_method_chaining_returns_self(self):
        """Test that methods return self for chaining."""
        cs = colour_str("test")

        # Each method should return the same object (allowing chaining)
        result1 = cs.red()
        result2 = result1.bright()
        result3 = result2.back_green()

        assert result1 is cs
        assert result2 is cs
        assert result3 is cs

    def test_empty_string(self):
        """Test with empty string."""
        cs = colour_str("")
        result = str(cs.red())
        expected = f"{Fore.RED}{Style.RESET_ALL}"
        assert result == expected

    def test_string_with_special_characters(self):
        """Test with special characters in string."""
        cs = colour_str("Hello\nWorld\t!")
        result = str(cs.green())
        expected = f"{Fore.GREEN}Hello\nWorld\t!{Style.RESET_ALL}"
        assert result == expected

    def test_reuse_after_string_conversion(self):
        """Test that object can be reused after string conversion."""
        cs = colour_str("test")

        # First conversion
        result1 = str(cs.red())
        expected1 = f"{Fore.RED}test{Style.RESET_ALL}"
        assert result1 == expected1

        # Note: The colour_str class accumulates codes, so this is expected behavior
        # Second conversion with new color - will include previous red code (order matters)
        result2 = str(cs.blue())
        expected2 = (
            f"{Fore.RED}{Fore.BLUE}test{Style.RESET_ALL}"  # red added first, then blue
        )
        assert result2 == expected2

    def test_all_colors_and_styles_combination(self):
        """Test combining all available colors and styles."""
        cs = colour_str("test")
        result = str(
            cs.red()
            .green()
            .blue()
            .yellow()
            .black()
            .back_red()
            .back_green()
            .back_blue()
            .back_yellow()
            .dim()
            .bright()
        )

        # Should contain all the style codes
        assert Fore.RED in result
        assert Fore.GREEN in result
        assert Fore.BLUE in result
        assert Fore.YELLOW in result
        assert Fore.BLACK in result
        assert Back.RED in result
        assert Back.GREEN in result
        assert Back.BLUE in result
        assert Back.YELLOW in result
        assert Style.DIM in result
        assert Style.BRIGHT in result
        assert Style.RESET_ALL in result
        assert result.endswith("test" + Style.RESET_ALL)

    def test_order_of_codes_preserved(self):
        """Test that the order of applied codes is preserved."""
        cs = colour_str("test")
        result = str(cs.red().dim().back_green())

        # Order should be: red, dim, back_green
        expected = f"{Fore.RED}{Style.DIM}{Back.GREEN}test{Style.RESET_ALL}"
        assert result == expected

    def test_large_string(self):
        """Test with large string."""
        large_text = "x" * 1000
        cs = colour_str(large_text)
        result = str(cs.yellow())
        expected = f"{Fore.YELLOW}{large_text}{Style.RESET_ALL}"
        assert result == expected
        assert len(result) == len(Fore.YELLOW) + len(large_text) + len(Style.RESET_ALL)

    def test_unicode_string(self):
        """Test with unicode characters."""
        unicode_text = "Hello 🌍 世界 🚀"
        cs = colour_str(unicode_text)
        result = str(cs.green())
        expected = f"{Fore.GREEN}{unicode_text}{Style.RESET_ALL}"
        assert result == expected
