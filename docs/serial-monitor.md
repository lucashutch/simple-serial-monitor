# 📡 Serial Monitor

Comprehensive guide for the serial port monitoring tool with interactive sending, logging, and advanced features.

## 🚀 Quick Start

```bash
# Basic monitoring (default port and baud)
monitor

# Interactive sending mode
monitor --send

# With specific configuration
monitor --port ACM0 --baud 9600 --log --highlight=error,warning
```

## 📖 Full Command Reference

### Options
```bash
usage: monitor [-h] [-p PORT] [-b BAUD] [-l] [-lf LOG_FILE] [-ld LOG_DIRECTORY] [-c] [-t {off,epoch,ms,dt}] [--highlight HIGHLIGHT] [--send]
```

### Detailed Parameters

| Option | Short | Long | Description | Example |
|---|---|---|---|
| Port | `-p` | `--port` | Serial port (ACM0, USB0, COM3) | `--port ACM2` |
| Baud Rate | `-b` | `--baud` | Serial rate (default: 115200) | `--baud 9600` |
| Log | `-l` | `--log` | Enable logging to file | `--log` |
| Log File | `-lf` | `--log-file` | Custom log filename | `--log-file test.log` |
| Log Directory | `-ld` | `--log-directory` | Log folder (default: ./logs) | `--log-directory /tmp/logs` |
| Clear | `-c` | `--clear` | Clear terminal on start | `--clear` |
| Timestamp | `-t` | `--print-time` | Timestamp format | `--print_time dt` |
| Highlight | `--highlight` | Comma-separated keywords | `--highlight=error,warning` |
| Send | `--send` | Enable interactive sending | `--send` |

### Timestamp Formats

| Format | Description | Example |
|---|---|---|
| `off` | No timestamp | `data received` |
| `epoch` | Unix timestamp with ms | `1672531200.123 data` |
| `ms` | Milliseconds since epoch | `1672531123 data` |
| `dt` | Human-readable datetime | `2023-01-01 10:00:00.123 data` |

## 🎯 Interactive Sending Mode

### Enabling Send Mode
```bash
# Basic interactive sending
monitor --send

# With additional features
monitor --send --log --print_time dt --highlight=error,warning
```

### How It Works
1. **Start monitor** with `--send` flag
2. **Type commands** and press Enter to send
3. **See sent data** in output with timestamps (if enabled)
4. **Both directions** logged when logging enabled
5. **Auto-reconnect** works for sending and receiving

### Sending Examples
```bash
# Connect to specific device
monitor --send --port COM3 --baud 115200

# With logging and keyword highlighting
monitor --send --log --highlight=ERROR,WARNING,FAIL

# With timestamps and clear terminal
monitor --send --log --print_time epoch --clear
```

## 📝 Logging Features

### Automatic Log Naming
Log files are automatically named with timestamp:
```
logs/
├── 2023.01.01_12.00.00_test.txt
├── 2023.01.01_14.30.45_test.txt
└── 2023.01.02_09.15.22_test.txt
```

### Log Formats
```bash
# No timestamp
data received
sent command

# Epoch timestamp
1672531200.123 data received
1672531200.456 sent command

# Datetime format
2023-01-01 10:00:00.123 data received
2023-01-01 10:00:00.456 sent command
```

### Custom Log Configuration
```bash
# Custom log file and directory
monitor -p ACM0 -b 2000000 -l -lf test_123 -ld /long_test_logs

# Results in: /long_test_logs/2023.01.01_12.00.00_test_123.txt
```

## 🎨 Advanced Features

### Keyword Highlighting
Highlight important words in real-time output:

```bash
# Basic highlighting
monitor --highlight=error,warning,fail

# Case-insensitive matching
monitor --highlight=ERROR,Warning,FAIL

# Technical debugging
monitor --highlight=timeout,disconnect,connected,initialized
```

### Auto-Reconnect
The monitor automatically reconnects when:
- Serial device is disconnected
- USB device is unplugged/replugged
- Connection is lost due to errors

### Cross-Platform Port Detection

| Platform | Common Port Names | Detection Method |
|---|---|---|
| Linux | `/dev/ttyACM0`, `/dev/ttyUSB0` | `ls /dev/tty*` |
| macOS | `/dev/cu.usbmodem*`, `/dev/tty.usbmodem*` | `ls /dev/cu.*` |
| Windows | `COM3`, `COM4` | Device Manager |

## 💡 Practical Examples

### 🏭 Embedded Development
```bash
# Monitor Arduino/ESP32 output with error highlighting
monitor --port ACM0 --baud 115200 --highlight=error,fail,timeout

# Send AT commands to cellular module
monitor --send --port COM7 --baud 115200 --log
```

### 🔧 Automation & Testing
```bash
# Automated testing with logging
monitor --send --log --print_time epoch --highlight=test,pass,fail

# Production monitoring
monitor --port /dev/ttyUSB1 --baud 921600 --log --clear
```

### 🐛 Debugging Scenarios
```bash
# Debug with maximum verbosity
monitor --send --log --print_time dt --highlight=debug,error,exception --clear

# Capture intermittent issues
monitor --log --highlight=disconnect,reconnect,timeout
```

## ⚠️ Troubleshooting

### Connection Issues
```bash
# Try different baud rates
monitor --port ACM0 --baud 9600
monitor --port ACM0 --baud 38400

# List available ports (Linux/macOS)
ls /dev/tty*
# Windows: Check Device Manager
```

### Permission Issues
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER

# Then logout and login again
monitor --send
```



## 🔧 Technical Details

### ANSI Code Stripping
When logging to files, ANSI escape codes are automatically stripped for clean logs.

### Signal Handling
The monitor handles:
- `SIGINT` (Ctrl+C) for graceful shutdown
- `SIGTERM` for system termination
- Proper thread cleanup and resource release

### Thread Architecture
- **Main Thread**: Serial port reading
- **Sender Thread**: Interactive input handling (if --send enabled)
- **Logging Thread**: Asynchronous file operations

For additional troubleshooting, see [Troubleshooting Guide](examples/troubleshooting.md).