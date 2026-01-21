"""Test CLI entry points and additional functionality."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

# Add src directory to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import the modules that contain the main functions
import src.embedded_cereal_bowl.cli as cli
import src.embedded_cereal_bowl.monitor.monitor as monitor
import src.embedded_cereal_bowl.timestamp.timestamp as timestamp
import src.embedded_cereal_bowl.formatter.formatter as formatter


class TestCLI:
    """Test cases for CLI entry points."""

    @patch("src.embedded_cereal_bowl.monitor.monitor.parse_arguments")
    @patch("src.embedded_cereal_bowl.monitor.monitor.run_serial_printing")
    def test_main_monitor_basic(self, mock_run, mock_parse):
        """Test basic monitor CLI entry point."""
        mock_args = Mock()
        mock_args.port = "ACM0"
        mock_args.baud = 115200
        mock_args.log = False
        mock_args.log_file = ""
        mock_args.log_directory = "/logs"
        mock_args.clear = False
        mock_args.print_time = "off"
        mock_args.highlight = None
        mock_args.send = False
        mock_parse.return_value = mock_args

        with patch("sys.argv", ["monitor"]):
            with patch("builtins.print"):
                cli.main_monitor()

        mock_parse.assert_called_once()
        mock_run.assert_called_once()

    @patch("src.embedded_cereal_bowl.timestamp.timestamp.parse_and_convert_time")
    def test_main_timestamp_success(self, mock_parse):
        """Test timestamp CLI entry point."""
        mock_parse.return_value = ("2023-01-01T12:30:45.567Z", "local", 1672573845.567)

        with patch("sys.argv", ["timestamp", "1672573845.567"]):
            with patch("builtins.print") as mock_print:
                cli.main_timestamp()

        mock_parse.assert_called_once_with("1672573845.567")
        mock_print.assert_called()

    @patch("src.embedded_cereal_bowl.timestamp.timestamp.parse_and_convert_time")
    def test_main_timestamp_error(self, mock_parse):
        """Test timestamp CLI entry point with error."""
        mock_parse.side_effect = ValueError("Invalid input")

        with patch("sys.argv", ["timestamp", "invalid"]):
            with patch("builtins.print") as mock_print:
                with patch("sys.exit") as mock_exit:
                    cli.main_timestamp()

        mock_parse.assert_called_once_with("invalid")
        mock_print.assert_called()
        mock_exit.assert_called_once()

    def test_main_formatter(self):
        """Test formatter CLI entry point."""
        with patch("sys.argv", ["format-code", "/test/path"]):
            with pytest.raises(SystemExit):
                cli.main_formatter()

    def test_main_check_crlf_not_implemented(self):
        """Test check-crlf CLI entry point (not yet implemented)."""
        with patch("sys.argv", ["check-crlf"]):
            with patch("sys.exit") as mock_exit:
                try:
                    cli.main_check_crlf()
                except SystemExit:
                    pass

            mock_exit.assert_called_once()  # May exit with different codes


class TestAdditionalModules:
    """Test cases for additional modules not covered elsewhere."""

    def test_archive_logs_import(self):
        """Test that archive_logs module can be imported."""
        try:
            from src.embedded_cereal_bowl import archive_logs

            assert hasattr(archive_logs, "main")
        except ImportError:
            pytest.fail("Could not import archive_logs module")

    def test_check_crlf_import(self):
        """Test that check_crlf module can be imported."""
        try:
            from src.embedded_cereal_bowl import check_crlf

            assert hasattr(check_crlf, "main")
        except ImportError:
            pytest.fail("Could not import check_crlf module")

    def test_utils_imports(self):
        """Test that utils modules can be imported."""
        try:
            from src.embedded_cereal_bowl.utils import color_utils

            assert color_utils.colour_str is not None
        except ImportError:
            pytest.fail("Could not import color_utils module")

    def test_all_main_functions_callable(self):
        """Test that all main functions are callable."""
        from src.embedded_cereal_bowl.cli import (
            main_monitor,
            main_timestamp,
            main_check_crlf,
            main_formatter,
        )

        assert callable(main_monitor)
        assert callable(main_timestamp)
        assert callable(main_check_crlf)
        assert callable(main_formatter)

    def test_module_versions(self):
        """Test that version info is accessible."""
        try:
            from src.embedded_cereal_bowl import __version__

            assert isinstance(__version__, str)
            assert len(__version__) > 0
        except (ImportError, AttributeError):
            pytest.skip("Version information not available")
