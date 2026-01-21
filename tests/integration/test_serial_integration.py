"""Integration tests with mocked serial ports."""

import os
import pytest
import sys
import threading
import time
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

# Add src directory to path for testing
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.embedded_cereal_bowl.monitor.monitor import (
    handle_user_input,
    serial_loop,
    run_serial_printing,
)


class TestHandleUserInputIntegration:
    """Integration tests for handle_user_input function."""

    @patch("src.embedded_cereal_bowl.monitor.monitor.select.select")
    @patch("sys.stdin.readline")
    @patch("src.embedded_cereal_bowl.monitor.monitor.send_serial_data")
    def test_handle_user_input_normal_operation(
        self, mock_send, mock_readline, mock_select
    ):
        """Test normal user input handling."""
        # Mock stdin to have input available
        mock_select.return_value = ([Mock()], [], [])
        mock_readline.side_effect = ["test command\n", KeyboardInterrupt()]
        mock_send.return_value = True

        mock_ser = Mock()
        stop_event = threading.Event()

        with patch(
            "threading.Event.wait", side_effect=[False, True]
        ):  # Stop after first iteration
            try:
                handle_user_input(mock_ser, "epoch", None, stop_event)
            except KeyboardInterrupt:
                pass

            # Verify the command was processed
            mock_readline.assert_called()
            mock_send.assert_called_once_with(mock_ser, "test command", "epoch", None)

    @patch("src.embedded_cereal_bowl.monitor.monitor.select.select")
    @patch("sys.stdin.readline")
    def test_handle_user_input_empty_line(self, mock_readline, mock_select):
        """Test handling of empty input lines."""
        mock_select.return_value = ([Mock()], [], [])
        mock_readline.return_value = "\n"  # Just a newline

        mock_ser = Mock()
        stop_event = threading.Event()

        with patch(
            "src.embedded_cereal_bowl.monitor.monitor.send_serial_data"
        ) as mock_send:
            thread = threading.Thread(
                target=handle_user_input,
                args=(mock_ser, "epoch", None, stop_event),
                daemon=True,
            )
            thread.start()

            time.sleep(0.1)
            stop_event.set()
            thread.join(timeout=1.0)

            # Should not send empty lines
            mock_send.assert_not_called()

    @patch("src.embedded_cereal_bowl.monitor.monitor.select.select")
    @patch("sys.stdin.readline")
    def test_handle_user_input_no_stdin_available(self, mock_readline, mock_select):
        """Test handling when stdin is not available."""
        mock_select.return_value = ([], [], [])  # No stdin available

        mock_ser = Mock()
        stop_event = threading.Event()

        with patch(
            "src.embedded_cereal_bowl.monitor.monitor.send_serial_data"
        ) as mock_send:
            thread = threading.Thread(
                target=handle_user_input,
                args=(mock_ser, "epoch", None, stop_event),
                daemon=True,
            )
            thread.start()

            time.sleep(0.1)
            stop_event.set()
            thread.join(timeout=1.0)

            # Should not attempt to read or send
            mock_readline.assert_not_called()
            mock_send.assert_not_called()


class TestSerialLoopIntegration:
    """Integration tests for serial_loop function."""

    @patch("src.embedded_cereal_bowl.monitor.monitor.send_serial_data")
    @patch("threading.Thread")
    @patch("src.embedded_cereal_bowl.monitor.monitor.colour_str")
    def test_serial_loop_with_send_enabled(self, mock_colour, mock_thread, mock_send):
        """Test serial loop with send functionality enabled."""
        # Mock the serial port
        mock_ser = Mock()
        mock_ser.readline.side_effect = [
            b"test data 1\n",
            b"test data 2\n",
            b"",  # Empty line to continue
            KeyboardInterrupt(),  # Exit the loop
        ]

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        mock_colour.return_value = "colored message"

        stop_event = threading.Event()

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.add_time_to_line",
                return_value="",
            ):
                try:
                    serial_loop(mock_ser, "epoch", None, None, True)
                except (KeyboardInterrupt, AttributeError):
                    pass  # Expected to exit

        # Verify input thread was started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @patch("src.embedded_cereal_bowl.monitor.monitor.create_replacement_lambda")
    @patch("src.embedded_cereal_bowl.monitor.monitor.colour_str")
    def test_serial_loop_with_highlighting(self, mock_colour, mock_replacement):
        """Test serial loop with word highlighting."""
        # Mock the serial port
        mock_ser = Mock()
        mock_ser.readline.side_effect = [
            b"ERROR: Something went wrong\n",
            b"WARNING: Be careful\n",
            KeyboardInterrupt(),
        ]

        mock_replacement.return_value = lambda m: "highlighted_error"
        mock_colour.return_value = "colored text"

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.add_time_to_line",
                return_value="",
            ):
                try:
                    serial_loop(mock_ser, "epoch", None, ["error", "warning"], False)
                except (KeyboardInterrupt, AttributeError):
                    pass

        # Verify replacement function was called for highlighting
        mock_replacement.assert_called()

    @patch("builtins.print")
    @patch("src.embedded_cereal_bowl.monitor.monitor.add_time_to_line")
    def test_serial_loop_with_logging(self, mock_add_time, mock_print):
        """Test serial loop with file logging."""
        mock_ser = Mock()
        mock_ser.readline.side_effect = [b"test log message\n", KeyboardInterrupt()]

        mock_file = Mock()
        mock_add_time.return_value = "timestamp: "

        try:
            serial_loop(mock_ser, "epoch", mock_file, None, False)
        except (KeyboardInterrupt, AttributeError):
            pass

        # Verify file write was called
        mock_file.write.assert_called()
        mock_print.assert_called()

    @patch("builtins.print")
    @patch("src.embedded_cereal_bowl.monitor.monitor.add_time_to_line")
    def test_serial_loop_ansi_escape_stripping(self, mock_add_time, mock_print):
        """Test that ANSI escape codes are stripped from log files."""
        mock_ser = Mock()
        mock_ser.readline.side_effect = [
            b"\x1b[31mred text\x1b[0m\n",
            KeyboardInterrupt(),
        ]

        mock_file = Mock()
        mock_add_time.return_value = "timestamp: "

        try:
            serial_loop(mock_ser, "epoch", mock_file, None, False)
        except (KeyboardInterrupt, AttributeError):
            pass

        # Verify ANSI codes were stripped from file write
        written_content = mock_file.write.call_args[0][0]
        assert "\x1b[31m" not in written_content
        assert "\x1b[0m" not in written_content


class TestRunSerialPrintingIntegration:
    """Integration tests for run_serial_printing function."""

    @patch("src.embedded_cereal_bowl.monitor.monitor.serial_loop")
    @patch("time.sleep")
    def test_run_serial_printing_successful_connection(self, mock_sleep, mock_loop):
        """Test successful serial connection and operation."""
        # Mock successful serial connection
        mock_ser = Mock()
        mock_ser.readline.side_effect = KeyboardInterrupt()  # Exit after first call

        with patch("serial.Serial") as mock_serial:
            mock_serial.return_value.__enter__.return_value = mock_ser
            mock_serial.return_value.__exit__.return_value = None

            with patch("builtins.print"):
                with patch(
                    "src.embedded_cereal_bowl.monitor.monitor.wait_with_spinner"
                ):
                    try:
                        run_serial_printing(
                            "/dev/ttyUSB0", 115200, "epoch", None, None, False
                        )
                    except KeyboardInterrupt:
                        pass  # Expected in test

        # Verify serial port was opened with correct parameters
        mock_serial.assert_called_with("/dev/ttyUSB0", 115200, timeout=0.05)

    @pytest.mark.skipif(
        os.environ.get("CI") == "true", reason="Hangs in CI due to infinite retry loop"
    )
    @patch("src.embedded_cereal_bowl.monitor.monitor.wait_with_spinner")
    @patch("time.sleep")
    @patch("src.embedded_cereal_bowl.monitor.monitor.colour_str")
    def test_run_serial_printing_connection_failure_retry(
        self, mock_colour, mock_sleep, mock_spinner
    ):
        """Test retry behavior when serial connection fails."""
        import serial

        # Mock serial exception (device not found)
        mock_spinner.return_value = 1
        mock_colour.return_value = "colored message"

        with patch("serial.Serial") as mock_serial:
            mock_serial.side_effect = serial.SerialException("Device not found")

            # Test that it tries to connect and shows spinner
            with patch("builtins.print"):
                try:
                    run_serial_printing(
                        "/dev/ttyUSB0", 115200, "epoch", None, None, False
                    )
                    time.sleep(0.1)  # Brief delay
                except KeyboardInterrupt:
                    pass

        # Should attempt to open serial port
        mock_serial.assert_called_with("/dev/ttyUSB0", 115200, timeout=0.05)

    @pytest.mark.skipif(os.environ.get("CI") == "true", reason="Hangs in CI")
    @patch("sys.exit")
    @patch("src.embedded_cereal_bowl.monitor.monitor.colour_str")
    def test_run_serial_printing_keyboard_interrupt(self, mock_colour, mock_exit):
        """Test graceful shutdown on keyboard interrupt."""
        import serial

        # Mock serial exception followed by keyboard interrupt
        mock_serial = Mock()
        mock_serial.Serial.side_effect = [
            serial.SerialException("Device not found"),
            KeyboardInterrupt(),
        ]

        mock_colour.return_value = "colored message"

        with patch(
            "src.embedded_cereal_bowl.monitor.monitor.serial.Serial", mock_serial
        ):
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.wait_with_spinner",
                return_value=1,
            ):
                run_serial_printing("/dev/ttyUSB0", 115200, "epoch", None, None, False)

        # Should exit gracefully
        mock_exit.assert_called_once_with(0)

    @patch("src.embedded_cereal_bowl.monitor.monitor.serial_loop")
    @patch("src.embedded_cereal_bowl.monitor.monitor.wait_with_spinner")
    @patch("time.sleep")
    def test_run_serial_printing_with_highlight_words(
        self, mock_sleep, mock_spinner, mock_loop
    ):
        """Test run_serial_printing with highlight words."""
        mock_serial = Mock()
        mock_serial.Serial.return_value.__enter__.return_value = mock_serial
        mock_spinner.return_value = 1

        highlight_words = ["error", "warning", "debug"]

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.serial.Serial", mock_serial
            ):
                try:
                    run_serial_printing(
                        "/dev/ttyUSB0", 115200, "epoch", None, highlight_words, False
                    )
                except (KeyError, AttributeError):
                    pass

        # Verify serial_loop was called with highlight words
        mock_loop.assert_called()
        args, kwargs = mock_loop.call_args
        assert len(args) >= 5
        assert args[4] == highlight_words  # highlight_words parameter

    @patch("src.embedded_cereal_bowl.monitor.monitor.serial_loop")
    @patch("src.embedded_cereal_bowl.monitor.monitor.wait_with_spinner")
    @patch("time.sleep")
    def test_run_serial_printing_with_send_enabled(
        self, mock_sleep, mock_spinner, mock_loop
    ):
        """Test run_serial_printing with send functionality enabled."""
        mock_serial = Mock()
        mock_serial.Serial.return_value.__enter__.return_value = mock_serial
        mock_spinner.return_value = 1

        with patch("builtins.print") as mock_print:
            with patch(
                "src.embedded_cereal_bowl.monitor.monitor.serial.Serial", mock_serial
            ):
                try:
                    run_serial_printing(
                        "/dev/ttyUSB0", 115200, "epoch", None, None, True
                    )
                except (KeyError, AttributeError):
                    pass

        # Verify serial_loop was called with send enabled
        mock_loop.assert_called()
        args, kwargs = mock_loop.call_args
        assert len(args) >= 6
        assert args[5] == True  # enable_send parameter
