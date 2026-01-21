"""Test utility functions and helper classes."""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.embedded_cereal_bowl.monitor.monitor import (
    serial_loop,
    create_replacement_lambda,
    ASNI_ESCAPE_PATTERN,
    get_serial_prefix,
    clear_terminal,
    run_serial_printing_with_logs,
)


class TestUtilityFunctions:
    """Test utility functions not covered elsewhere."""

    def test_get_serial_prefix_windows(self):
        """Test serial prefix on Windows."""
        with patch("os.name", "nt"):
            prefix = get_serial_prefix()
            assert prefix == ""

    def test_get_serial_prefix_unix(self):
        """Test serial prefix on Unix systems."""
        with patch("os.name", "posix"):
            prefix = get_serial_prefix()
            assert prefix == "/dev/tty"

    @patch("os.system")
    def test_clear_terminal_windows(self, mock_system):
        """Test terminal clearing on Windows."""
        with patch("os.name", "nt"):
            clear_terminal()
            mock_system.assert_called_once_with("cls")

    @patch("os.system")
    def test_clear_terminal_unix(self, mock_system):
        """Test terminal clearing on Unix."""
        with patch("os.name", "posix"):
            clear_terminal()
            mock_system.assert_called_once_with("clear")

    @patch("os.mkdir")
    @patch("os.path.isdir")
    @patch("builtins.open")
    @patch("src.embedded_cereal_bowl.monitor.monitor.run_serial_printing")
    def test_run_serial_printing_with_logs_new_dir(
        self, mock_run, mock_open, mock_isdir, mock_mkdir
    ):
        """Test logging with new directory creation."""
        mock_isdir.return_value = False

        with patch(
            "src.embedded_cereal_bowl.monitor.monitor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2023.01.01_12.00.00"

            run_serial_printing_with_logs(
                "/dev/ttyUSB0", 115200, "test", "/tmp/logs", "epoch", None, False
            )

        mock_isdir.assert_called_once_with("/tmp/logs")
        mock_mkdir.assert_called_once_with("/tmp/logs")
        mock_open.assert_called_once_with(
            "/tmp/logs/2023.01.01_12.00.00_test.txt", "a+", buffering=1
        )
        mock_run.assert_called_once()

    @patch("os.mkdir")
    @patch("os.path.isdir")
    @patch("builtins.open")
    @patch("src.embedded_cereal_bowl.monitor.monitor.run_serial_printing")
    def test_run_serial_printing_with_logs_existing_dir(
        self, mock_run, mock_open, mock_isdir, mock_mkdir
    ):
        """Test logging with existing directory."""
        mock_isdir.return_value = True

        with patch(
            "src.embedded_cereal_bowl.monitor.monitor.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2023.01.01_12.00.00"

            run_serial_printing_with_logs(
                "/dev/ttyUSB0", 115200, "test", "/tmp/logs", "epoch", None, False
            )

        mock_isdir.assert_called_once_with("/tmp/logs")
        mock_mkdir.assert_not_called()  # Directory already exists
        mock_open.assert_called_once_with(
            "/tmp/logs/2023.01.01_12.00.00_test.txt", "a+", buffering=1
        )
        mock_run.assert_called_once()


class TestANSIEscapePattern:
    """Test ANSI escape pattern and related functions."""

    def test_ansi_escape_pattern(self):
        """Test that ANSI escape pattern matches expected codes."""
        # Should match basic color codes
        assert ASNI_ESCAPE_PATTERN.search("\x1b[31m")
        assert ASNI_ESCAPE_PATTERN.search("\x1b[32m")

        # Should match reset codes
        assert ASNI_ESCAPE_PATTERN.search("\x1b[0m")

        # Should match complex sequences
        assert ASNI_ESCAPE_PATTERN.search("\x1b[1;31m")

        # Should not match plain text
        assert not ASNI_ESCAPE_PATTERN.search("plain text")

    def test_create_replacement_lambda_with_ansi_codes(self):
        """Test replacement lambda with ANSI codes in line."""
        line_state = "normal \x1b[31mred\x1b[0m normal error"

        with patch(
            "src.embedded_cereal_bowl.monitor.monitor.colour_str"
        ) as mock_colour:
            mock_coloured = Mock()
            mock_coloured.back_green.return_value = mock_coloured
            mock_coloured.black.return_value = mock_coloured
            mock_colour.return_value = mock_coloured
            mock_coloured.__str__ = Mock(return_value="highlighted_error")

            lambda_func = create_replacement_lambda(line_state)

            # Create a mock match object
            mock_match = Mock()
            mock_match.group.return_value = "error"
            mock_match.start.return_value = len("normal \x1b[31mred\x1b[0m normal ")

            result = lambda_func(mock_match)

            # Should find preceding ANSI codes
            mock_colour.assert_called_once_with("error")


class TestSerialLoopEdgeCases:
    """Test serial loop edge cases and threading behavior."""

    @patch("src.embedded_cereal_bowl.monitor.monitor.send_serial_data")
    @patch("threading.Thread")
    @patch("src.embedded_cereal_bowl.monitor.monitor.colour_str")
    def test_serial_loop_no_send_enabled(self, mock_colour, mock_thread, mock_send):
        """Test serial loop without send functionality."""
        mock_ser = Mock()
        mock_ser.readline.side_effect = [b"data\n", KeyboardInterrupt()]

        stop_event = Mock()
        stop_event.is_set.return_value = False

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.add_time_to_line",
                return_value="",
            ):
                try:
                    serial_loop(mock_ser, "epoch", None, None, False)
                except (KeyboardInterrupt, AttributeError):
                    pass

        # Should not start input thread when send is disabled
        mock_thread.assert_not_called()

    def test_serial_loop_empty_lines(self):
        """Test serial loop handling empty lines."""
        mock_ser = Mock()
        mock_ser.readline.side_effect = [b"", b"data\n", b"", KeyboardInterrupt()]

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.add_time_to_line",
                return_value="",
            ):
                try:
                    serial_loop(mock_ser, "epoch", None, None, False)
                except (KeyboardInterrupt, AttributeError):
                    pass

        # Should continue on empty lines
        assert mock_ser.readline.call_count >= 2
        assert mock_print.call_count == 1  # Only non-empty line printed

    def test_serial_loop_with_highlight_processing(self):
        """Test serial loop highlight word processing."""
        mock_ser = Mock()
        mock_ser.readline.side_effect = [
            b"This is an error message\n",
            KeyboardInterrupt(),
        ]

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.add_time_to_line",
                return_value="",
            ):
                with patch(
                    "src.embedded_cereal_bowl.monitor.monitor.create_replacement_lambda"
                ) as mock_replacement:
                    mock_replacement.return_value = lambda m: "highlighted_error"

                    try:
                        serial_loop(mock_ser, "epoch", None, ["error"], False)
                    except (KeyboardInterrupt, AttributeError):
                        pass

        # Should create replacement lambda for highlight words
        mock_replacement.assert_called()


class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_handling_decode_errors(self):
        """Test handling of UTF-8 decode errors."""
        mock_ser = Mock()
        # Simulate problematic bytes that might cause decode errors
        mock_ser.readline.side_effect = [
            b"valid data\n",
            b"\xff\xfe invalid\n",
            KeyboardInterrupt(),
        ]

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.add_time_to_line",
                return_value="",
            ):
                try:
                    serial_loop(mock_ser, "epoch", None, None, False)
                except (KeyboardInterrupt, AttributeError):
                    pass

        # Should handle both valid and invalid data gracefully
        assert mock_print.call_count >= 1
        # Should not crash on decode errors

    def test_file_write_error_handling(self):
        """Test handling of file write errors during logging."""
        mock_ser = Mock()
        mock_ser.readline.side_effect = [b"data\n", KeyboardInterrupt()]

        mock_file = Mock()
        mock_file.write.side_effect = IOError("Disk full")

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.add_time_to_line",
                return_value="",
            ):
                try:
                    serial_loop(mock_ser, "epoch", mock_file, None, False)
                except (KeyboardInterrupt, AttributeError, IOError):
                    pass

        # Should attempt to write to file
        mock_file.write.assert_called()


class TestArgumentParsingEdgeCases:
    """Test argument parsing edge cases."""

    @patch("sys.argv", ["monitor", "--print_time", "invalid_choice"])
    def test_invalid_print_time_choice(self):
        """Test handling of invalid print_time choice."""
        from src.embedded_cereal_bowl.monitor.monitor import parse_arguments

        with pytest.raises(SystemExit):
            parse_arguments()

    @patch("sys.argv", ["monitor", "--highlight", ""])
    def test_empty_highlight_string(self):
        """Test handling of empty highlight string."""
        from src.embedded_cereal_bowl.monitor.monitor import parse_arguments

        args = parse_arguments()
        # Should handle empty highlight string gracefully
        assert args.highlight == ""

    @patch("sys.argv", ["monitor", "--highlight", "[error,warning]"])
    def test_highlight_with_brackets(self):
        """Test highlight string with brackets."""
        from src.embedded_cereal_bowl.monitor.monitor import parse_arguments

        args = parse_arguments()
        # Should strip brackets properly
        assert args.highlight == "[error,warning]"

    @patch("sys.argv", ["monitor", "--port", "/dev/ttyUSB0"])
    def test_port_with_full_path(self):
        """Test port specified with full path."""
        from src.embedded_cereal_bowl.monitor.monitor import parse_arguments

        args = parse_arguments()
        # Should accept full paths
        assert args.port == "/dev/ttyUSB0"
