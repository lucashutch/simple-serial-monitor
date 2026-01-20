"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add src directory to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_serial_port():
    """Mock serial port fixture for testing."""
    from unittest.mock import Mock
    mock_ser = Mock()
    mock_ser.readline.return_value = b"test data\n"
    mock_ser.write.return_value = None
    return mock_ser


@pytest.fixture
def mock_file_handle():
    """Mock file handle fixture for testing."""
    from unittest.mock import Mock
    mock_file = Mock()
    mock_file.write.return_value = None
    mock_file.close.return_value = None
    return mock_file


@pytest.fixture
def sample_test_data():
    """Sample test data for various test cases."""
    return {
        "timestamps": {
            "seconds": "1672531200.0",
            "milliseconds": "1672531200123",
            "with_ms": "1672531200.123",
            "iso_utc": "2023-01-01T00:00:00.000Z",
            "iso_with_offset": "2023-01-01T12:00:00.000+10:00",
            "iso_no_tz": "2023-01-01T12:00:00.000"
        },
        "serial_data": {
            "normal": b"normal serial data\n",
            "with_ansi": b"\x1b[31mred text\x1b[0m\n",
            "empty": b"",
            "unicode": b"unicode test \xe2\x9c\x93\n"
        },
        "highlight_words": ["error", "warning", "debug", "fail"],
        "file_extensions": [".cpp", ".h", ".hpp", ".c", ".cc", ".cxx", ".cmake"]
    }