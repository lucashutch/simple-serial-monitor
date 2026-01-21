# 🗓️ Timestamp Converter

Convert Unix timestamps and ISO 8601 strings to human-readable UTC and local time formats.

## 🚀 Quick Start

```bash
# Convert Unix timestamp (seconds)
timestamp 1761660634

# Convert Unix timestamp (milliseconds)  
timestamp 1761660634104

# Convert ISO 8601 string
timestamp "2025-01-21T14:10:34.104Z"
```

## 📖 Input Formats

### Unix Timestamps
| Format | Description | Example |
|---|---|---|
| Seconds | Standard Unix timestamp | `1761660634` |
| Milliseconds | Unix timestamp with ms | `1761660634104` |
| Microseconds | High precision timestamp | `1761660634104567` |

### ISO 8601 Strings
| Format | Description | Example |
|---|---|---|
| UTC with Z | `2025-01-21T14:10:34.104Z` | |
| UTC no Z | `2025-01-21T14:10:34.104` | |
| With timezone | `2025-01-21T14:10:34.104+10:00` | |
| Date only | `2025-01-21` | |
| With milliseconds | `2025-01-21T14:10:34.123` | |

## 📊 Output Examples

### Unix Timestamp Input
```bash
$ timestamp 1761660634
UTC:   2025-10-27T00:10:34.000Z
Local: 2025-10-27T10:10:34.104+10:00 (Australia/Sydney)

$ timestamp 1761660634104
UTC:   2025-10-27T00:10:34.104Z
Local: 2025-10-27T10:10:34.104+10:00 (Australia/Sydney)
```

### ISO 8601 String Input
```bash
$ timestamp "2025-01-21T14:10:34.104Z"
UTC:   2025-01-21T14:10:34.104Z
Local: 2025-01-22T00:10:34.104+10:00 (Australia/Sydney)

$ timestamp "2025-01-21T14:10:34.104+10:00"
UTC:   2025-01-21T04:10:34.104Z
Local: 2025-01-21T14:10:34.104+10:00 (Australia/Sydney)
```

## 🌍 Timezone Handling

### Automatic Detection
The converter:
- Uses system's local timezone
- Shows timezone offset in output
- Handles daylight saving time automatically

### Examples by Region
```bash
# Input (same timestamp in UTC)
$ timestamp 1672531200

# Output varies by system timezone:
# UTC:    2023-01-01T00:00:00.000Z
# PST:     2022-12-31T16:00:00.000-08:00 (America/Los_Angeles)
# EST:     2022-12-31T19:00:00.000-05:00 (America/New_York)
# JST:     2023-01-01T09:00:00.000+09:00 (Asia/Tokyo)
# AEDT:    2023-01-01T11:00:00.000+11:00 (Australia/Sydney)
```

## 🔢 Precision Handling

### Millisecond Truncation
```bash
# High precision input
timestamp 1672531200.123456789

# Output truncated to 3 decimal places
UTC:   2023-01-01T00:00:00.123Z
```

### Supported Ranges
| Type | Range | Notes |
|---|---|---|
| 32-bit Unix | ±68 years (1901-2038) | Limited range |
| 64-bit Unix | ±292 billion years | Practical infinite |
| ISO 8601 | Any valid date | Full datetime support |

## 💡 Practical Examples

### 🏭 Embedded Development
```bash
# Convert Arduino millis() output
timestamp 1672531200

# Convert ESP32 timestamp
timestamp 1761660634104

# Parse log timestamps
grep "timestamp:" log.txt | awk '{print $2}' | xargs -I {} timestamp {}
```

### 🔧 Log Analysis
```bash
# Convert multiple timestamps
timestamps=(
  "1672531200"
  "1672534800" 
  "1672538400"
)
for ts in "${timestamps[@]}"; do
  timestamp "$ts"
done
```

### 📊 Data Processing
```bash
# CSV timestamp conversion
cat data.csv | cut -d',' -f1 | while read ts; do
  timestamp "$ts" | grep "UTC:" | cut -d' ' -f2
done

# Batch file processing
while read -r line; do
  if [[ $line =~ ^[0-9] ]]; then
    timestamp "$line"
  fi
done < timestamps.txt
```

### 🔍 Debugging Scenarios
```bash
# Validate timestamp format
timestamp "invalid-input"
# Error: Invalid timestamp format

# Edge cases
timestamp 0
# UTC:   1970-01-01T00:00:00.000Z
# Local: 1970-01-01T10:00:00.000+10:00

# Future dates
timestamp 4102444800
# UTC:   2100-01-01T00:00:00.000Z
```

## 🔧 Technical Details

### Supported ISO 8601 Variants
- `YYYY-MM-DDTHH:MM:SS.sssZ`
- `YYYY-MM-DDTHH:MM:SS.sss+HH:MM`
- `YYYY-MM-DDTHH:MM:SS.sss-HH:MM`
- `YYYY-MM-DD`
- With optional milliseconds

### Unix Timestamp Detection
```bash
# Automatic detection based on length
if [ ${#timestamp} -gt 10 ]; then
  # Assume milliseconds (11+ digits)
else
  # Assume seconds (10 digits or less)
fi
```

### Error Handling
- Invalid format detection
- Out-of-range timestamps
- Malformed ISO strings
- Clear error messages


## ⚠️ Troubleshooting

### Common Issues
```bash
# Invalid timezone (system issue)
export TZ="UTC"
timestamp 1672531200

# Python version issues
python3 --version  # Ensure Python 3.8+

# Permission issues
chmod +x timestamp  # Make script executable
```

### Validation Examples
```bash
# Test edge cases
timestamp 0                    # Epoch start
timestamp 4102444800          # Year 2100
timestamp -86400              # 1969-12-31

# Invalid input handling
timestamp "not a timestamp"     # Should show clear error
timestamp "2025-13-45"        # Invalid date
```