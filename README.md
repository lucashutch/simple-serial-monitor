# **🔧 Embedded Cereal Bowl**

A collection of lightweight Python utilities designed to simplify common embedded development and maintenance tasks, including **serial monitoring**, **code formatting**, **line ending checks**, and **timestamp conversion**.

## **📜 License**

This project is licensed under the **MIT License**.

## **💻 1. Simple Serial Monitor (monitor)**

A versatile serial monitor for reading and optionally writing to serial ports, with features like **logging**, **auto-reconnect**, and **highlighting** of specific keywords.

### **Usage**
```
usage: monitor [-h] [-p PORT] [-b BAUD] [-l] [-lf LOG_FILE] [-ld LOG_DIRECTORY] [-c] [-t {off,epoch,ms,dt}] [--highlight HIGHLIGHT]

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
```

### **Examples**

#### **Collect logs with default port and baud rate (/dev/ACM0 @ 115'200)**
```
./monitor
```
#### **Collect logs from serial GPS (/dev/ACM2 @ 9600)**
```
./monitor --port ACM2 --baud 9600
```
#### **Collect logs from a device (/dev/ACM0 @ 2'000'000) and save to /long_test_logs/[date]_test_123.txt**
```
./monitor -p ACM0 -b 2000000 -l -lf test_123 -ld /long_test_logs
```
## **✨ 2. Universal Code Formatter (formatter.py)**

A parallelized script to **automatically format** various source files in a project (C++, CMake, etc.) using external tools like clang-format and cmake-format. It can run in check-only mode to find unformatted files.

### **Supported Tools**

| Tool | File Extensions | File Names |
| :---- | :---- | :---- |
| **clang-format** | .h, .hpp, .hxx, .hh, .c, .cpp, .cxx, .cc | N/A |
| **cmake-format** | .cmake | CMakeLists.txt |

### **Usage**
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
## **🗓️ 3. Time Converter (timestamp)**

A command-line tool to convert a Unix timestamp (in seconds or milliseconds) or an ISO 8601 string into **human-readable UTC and local time** ISO 8601 formats.

### **Usage**
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

### **Usage**
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
