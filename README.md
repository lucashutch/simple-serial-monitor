# **🔧 Embedded Cereal Bowl**

A collection of lightweight Python utilities designed to simplify common embedded development and maintenance tasks, including **serial monitoring**, **code formatting**, **line ending checks**, and **timestamp conversion**.

## **📋 Table of Contents**

- [📜 License](#-license)
- [🚀 Quick Start](#-quick-start)
- [📦 Dependencies](#-dependencies)
- [💻 Serial Monitor](#-simple-serial-monitor-monitor)
- [✨ Code Formatter](#-universal-code-formatter-formatterpy)
- [🗓️ Time Converter](#️-time-converter-timestamp)
- [⚠️ Line Ending Check](#️-crlf-line-ending-check-check_crlfpy)

## **📜 License**

This project is licensed under the **MIT License**.

## **🚀 Quick Start**

```bash
# Clone the repository
git clone https://github.com/lucashutch/simple-serial-monitor.git
cd simple-serial-monitor

# Install dependencies
pip install pyserial regex colorama

# Make the scripts executable
chmod +x monitor timestamp

# Start monitoring (default port: ACM0/COM3 @ 115200)
./monitor

# Start with interactive sending
./monitor --send
```

## **📦 Dependencies**

The serial monitor requires the following Python packages:

```bash
pip install pyserial regex colorama
```

- **pyserial**: Serial communication library
- **regex**: Advanced regex for keyword highlighting
- **colorama**: Cross-platform colored terminal output

### **🔧 Installation**

```bash
# Install all dependencies at once
pip install pyserial regex colorama

# Or install from requirements.txt (if available)
pip install -r requirements.txt
```

## **💻 1. Simple Serial Monitor (monitor)**

A versatile serial monitor for **reading and writing** to serial ports, with features like **interactive sending**, **logging**, **auto-reconnect**, and **highlighting** of specific keywords.

### **✨ Key Features**
- **📡 Bidirectional Communication**: Read and send serial data simultaneously
- **🔄 Auto-Reconnect**: Automatically reconnects when connection is lost
- **📝 Logging**: Save serial data to timestamped log files
- **🎨 Keyword Highlighting**: Highlight important words in output
- **⏰ Timestamps**: Multiple timestamp formats available
- **🖥️ Cross-Platform**: Works on Windows, Linux, and macOS

### **📖 Usage**
```
usage: monitor [-h] [-p PORT] [-b BAUD] [-l] [-lf LOG_FILE] [-ld LOG_DIRECTORY] [-c] [-t {off,epoch,ms,dt}] [--highlight HIGHLIGHT] [--send]

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Specify the serial port to connect to,
                        e.g., ACM0, USB0 (Linux/macOS), or COM3 (Windows)
  -b BAUD, --baud BAUD  Baud rate to set the serial port to (default: 115200)
  -l, --log             Save serial port data to a log file
  -lf LOG_FILE, --log-file LOG_FILE
                        Filename used to save log files. Will appear as date_time_<filename>.txt
  -ld LOG_DIRECTORY, --log-directory LOG_DIRECTORY
                        Folder to save logging file (default: ./logs)
  -c, --clear           Clear terminal before printing
  -t {off,epoch,ms,dt}, --print_time {off,epoch,ms,dt}
                        Print system time on each log line:
                          off   - No timestamp
                          epoch - Unix timestamp with ms (e.g., 1672531200.123)
                          ms    - Milliseconds since epoch
                          dt    - Human-readable datetime (e.g., 2023-01-01 10:00:00.123)
  --highlight HIGHLIGHT
                        Comma-separated list of words to highlight (case-insensitive).
                        Example: --highlight=error,warning,fail
  --send                Enable interactive sending mode - type commands to send to serial device
```

### **🎯 Interactive Sending Mode**

The new `--send` flag enables bidirectional communication, allowing you to send commands to the serial device while monitoring incoming data:

```bash
# Enable interactive sending
./monitor --send

# With specific port and baud rate
./monitor --send --port ACM0 --baud 9600

# With logging and timestamps
./monitor --send --log --print_time dt

# With keyword highlighting
./monitor --send --highlight=error,warning
```

**How it works:**
1. Run monitor with `--send` flag
2. When connected, type commands and press Enter to send
3. Sent data appears in output with timestamps (if enabled)
4. Both sent and received data are logged (if logging enabled)
5. Auto-reconnect works for both sending and receiving

### **💡 Examples**

#### **📡 Basic Monitoring**
```bash
# Monitor with default settings (ACM0/COM3 @ 115200)
./monitor

# Monitor specific port and baud rate
./monitor --port ACM2 --baud 9600
```

#### **🎯 Interactive Sending**
```bash
# Enable interactive sending mode
./monitor --send

# Send commands with logging and timestamps
./monitor --send --log --print_time dt

# Send with keyword highlighting
./monitor --send --highlight=error,warning,fail
```

#### **📝 Logging & Timestamps**
```bash
# Save logs with timestamps
./monitor --log --print_time dt

# Custom log file and directory
./monitor -p ACM0 -b 2000000 -l -lf test_123 -ld /long_test_logs

# Unix timestamp format
./monitor --log --print_time epoch
```

#### **🎨 Advanced Features**
```bash
# Clear terminal and highlight keywords
./monitor --clear --highlight=ERROR,WARNING,FAIL

# Combine multiple features
./monitor --send --log --print_time dt --highlight=error --clear
```
## **✨ 2. Universal Code Formatter (formatter.py)**

A parallelized script to **automatically format** various source files in a project (C++, CMake, etc.) using external tools like clang-format and cmake-format. It can run in check-only mode to find unformatted files.

### **🛠️ Supported Tools**

| Tool | File Extensions | File Names |
| :---- | :---- | :---- |
| **clang-format** | .h, .hpp, .hxx, .hh, .c, .cpp, .cxx, .cc | N/A |
| **cmake-format** | .cmake | CMakeLists.txt |

### **📖 Usage**
```
usage: formatter.py [-h] [-i DIR [DIR ...]] [-j JOBS] [-v] [--check] [root_dir]

positional arguments:
  root_dir              The root directory to scan (default: current directory)

options:
  -h, --help            show this help message and exit
  --ignore -i DIR [DIR ...]
                        One or more directories to ignore.
                        (e.g., --ignore build third-party)
  -j, --jobs JOBS       The number of concurrent jobs to run.
                        (default: all available CPU cores)
  -v, --verbose         Enable verbose output.
  --check, -c           Run in 'check only' mode. Outputs files requiring changes and
                        the associated required changes
```

### **💡 Examples**
```bash
# Format current directory
python formatter.py

# Check formatting without making changes
python formatter.py --check

# Format specific directory with 4 parallel jobs
python formatter.py /path/to/project --jobs 4

# Ignore specific directories
python formatter.py --ignore build third-party --verbose
```
## **🗓️ 3. Time Converter (timestamp)**

A command-line tool to convert a Unix timestamp (in seconds or milliseconds) or an ISO 8601 string into **human-readable UTC and local time** ISO 8601 formats.

### **📖 Usage**
```
usage: timestamp [-h] time_input

positional arguments:
  time_input  Time value (e.g., 1761660634.104 or 2025-10-26T14:10:34.104Z)

options:
  -h, --help  Show this help message and exit
```

### **💡 Examples**
```bash
# Convert Unix timestamp (seconds)
./timestamp 1761660634

# Convert Unix timestamp (milliseconds)
./timestamp 1761660634104

# Convert ISO 8601 string
./timestamp "2025-10-26T14:10:34.104Z"

# Output example:
# UTC:   2025-10-26T14:10:34.104Z
# Local: 2025-10-27T00:10:34.104+10:00 (Example local timezone)
```
usage: timestamp [-h] time_input

positional arguments:
  time_input  Time value (e.g., 1761660634.104 or 2025-10-26T14:10:34.104Z)

options:
  -h, --help  show this help message and exit
```
### **Example**
```
./timestamp 1761660634104
UTC:   2025-10-26T14:10:34.104Z
Local: 2025-10-27T00:10:34.104+10:00 (Example local timezone)
```
## **⚠️ 4. CRLF Line Ending Check (check_crlf.py)**

A simple script to scan a directory for files that incorrectly use **CRLF** (\r\n) line endings instead of the standard **LF** (\n), which can cause issues in cross-platform development.

### **📖 Usage**
```
usage: check_crlf.py [-h] [--ignore DIR [DIR ...]] [-v] [root_dir]

positional arguments:
  root_dir              The root directory to scan (default: current directory)

options:
  -h, --help            show this help message and exit
  --ignore -i DIR [DIR ...]
                        One or more directories to ignore.
                        (e.g., --ignore build third-party)
  -v, --verbose         Enable verbose output.
```

### **💡 Examples**
```bash
# Check current directory
python check_crlf.py

# Check specific directory
python check_crlf.py /path/to/project

# Ignore specific directories
python check_crlf.py --ignore build third-party --verbose

# Common use case for git repositories
python check_crlf.py --ignore .git build
```

## **🤝 Contributing**

Contributions are welcome! Feel free to submit issues and pull requests to improve these utilities.

## **📞 Support**

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/lucashutch/simple-serial-monitor/issues).

---

**⭐ Star this repository if you find these utilities helpful!**
