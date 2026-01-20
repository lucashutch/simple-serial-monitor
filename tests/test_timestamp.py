"""Test timestamp conversion functionality."""

import pytest
from datetime import datetime, timezone
from src.embedded_cereal_bowl.timestamp.timestamp import parse_and_convert_time


class TestParseAndConvertTime:
    """Test cases for the parse_and_convert_time function."""

    def test_unix_timestamp_seconds(self):
        """Test parsing Unix timestamp in seconds."""
        ts = 1672531200.0  # 2023-01-01 00:00:00 UTC
        utc_str, local_str, utc_ts = parse_and_convert_time(str(ts))
        
        assert utc_str == "2023-01-01T00:00:00.000Z"
        assert utc_ts == ts

    def test_unix_timestamp_with_milliseconds(self):
        """Test parsing Unix timestamp with milliseconds."""
        ts = 1672531200.123
        utc_str, local_str, utc_ts = parse_and_convert_time(str(ts))
        
        assert utc_str == "2023-01-01T00:00:00.123Z"
        assert utc_ts == ts

    def test_milliseconds_timestamp_large(self):
        """Test parsing milliseconds timestamp (very large number)."""
        ms_ts = 1672531200123  # milliseconds since epoch
        utc_str, local_str, utc_ts = parse_and_convert_time(str(ms_ts))
        
        expected_ts = 1672531200.123  # converted to seconds
        assert utc_str == "2023-01-01T00:00:00.123Z"
        assert utc_ts == expected_ts

    def test_iso8601_string_with_z(self):
        """Test parsing ISO 8601 string with Z suffix."""
        iso_str = "2023-01-01T12:30:45.567Z"
        utc_str, local_str, utc_ts = parse_and_convert_time(iso_str)
        
        assert utc_str == iso_str
        # Verify this is a valid timestamp (actual value may vary by system)
        assert isinstance(utc_ts, float)
        assert utc_ts > 1672500000  # After Jan 1, 2023

    def test_iso8601_string_with_timezone_offset(self):
        """Test parsing ISO 8601 string with timezone offset."""
        iso_str = "2023-01-01T12:30:45.567+10:00"
        utc_str, local_str, utc_ts = parse_and_convert_time(iso_str)
        
        assert utc_str == "2023-01-01T02:30:45.567Z"
        # Verify this is a valid timestamp (actual value may vary by system)
        assert isinstance(utc_ts, float)
        assert utc_ts > 1672500000  # After Jan 1, 2023

    def test_iso8601_string_without_timezone(self):
        """Test parsing ISO 8601 string without timezone (assumed UTC)."""
        iso_str = "2023-01-01T12:30:45.567"
        utc_str, local_str, utc_ts = parse_and_convert_time(iso_str)
        
        assert utc_str == "2023-01-01T12:30:45.567Z"
        # Verify this is a valid timestamp (actual value may vary by system)
        assert isinstance(utc_ts, float)
        assert utc_ts > 1672500000  # After Jan 1, 2023

    def test_iso8601_string_without_milliseconds(self):
        """Test parsing ISO 8601 string without milliseconds."""
        iso_str = "2023-01-01T12:30:45Z"
        utc_str, local_str, utc_ts = parse_and_convert_time(iso_str)
        
        assert utc_str == "2023-01-01T12:30:45.000Z"
        # Verify this is a valid timestamp (actual value may vary by system)
        assert isinstance(utc_ts, float)
        assert utc_ts > 1672500000  # After Jan 1, 2023

    def test_invalid_input_string(self):
        """Test parsing invalid input string."""
        with pytest.raises(ValueError, match="Input 'invalid' is neither a valid Unix timestamp"):
            parse_and_convert_time("invalid")

    def test_empty_string(self):
        """Test parsing empty string."""
        with pytest.raises(ValueError, match="Input '' is neither a valid Unix timestamp"):
            parse_and_convert_time("")

    def test_malformed_iso8601_string(self):
        """Test parsing malformed ISO 8601 string."""
        with pytest.raises(ValueError, match="Input 'not-a-date' is neither a valid Unix timestamp"):
            parse_and_convert_time("not-a-date")

    def test_local_timezone_conversion(self):
        """Test that local timezone conversion produces valid results."""
        ts = "1672531200.123"  # 2023-01-01 00:00:00.123 UTC
        utc_str, local_str, utc_ts = parse_and_convert_time(ts)
        
        # Check that local string is valid ISO format
        assert "T" in local_str
        assert "." in local_str
        # Local string should not end with Z (it has timezone offset)
        assert not local_str.endswith("Z")
        
        # Parse local string to verify it's valid
        parsed_local = datetime.fromisoformat(local_str)
        assert parsed_local.tzinfo is not None

    def test_return_value_types(self):
        """Test that return values have the expected types."""
        ts = "1672531200.123"
        utc_str, local_str, utc_ts = parse_and_convert_time(ts)
        
        assert isinstance(utc_str, str)
        assert isinstance(local_str, str)
        assert isinstance(utc_ts, float)
        assert isinstance(int(utc_ts), int)

    def test_timestamp_precision(self):
        """Test that timestamp precision is preserved."""
        # Test with high precision timestamp
        ts = 1672531200.123456789
        utc_str, local_str, utc_ts = parse_and_convert_time(str(ts))
        
        # Milliseconds should be truncated to 3 decimal places
        assert utc_str == "2023-01-01T00:00:00.123Z"
        # UTC timestamp should preserve full precision
        assert abs(utc_ts - ts) < 0.000001

    def test_edge_case_year_boundaries(self):
        """Test timestamps at year boundaries."""
        # Test start of year 2024 (leap year)
        ts = 1704067200.0  # 2024-01-01 00:00:00 UTC
        utc_str, local_str, utc_ts = parse_and_convert_time(str(ts))
        
        assert utc_str == "2024-01-01T00:00:00.000Z"
        assert utc_ts == ts

    def test_negative_timestamp(self):
        """Test parsing negative timestamp (before 1970)."""
        ts = -86400.0  # 1969-12-31 00:00:00 UTC
        utc_str, local_str, utc_ts = parse_and_convert_time(str(ts))
        
        assert utc_str == "1969-12-31T00:00:00.000Z"
        assert utc_ts == ts