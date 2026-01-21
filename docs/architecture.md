# 🏗️ Project Architecture

Technical architecture and design decisions for Embedded Cereal Bowl tools.

## 📋 Architecture Overview

### Core Design Principles
- **Modular**: Each tool is standalone with minimal dependencies
- **Cross-Platform**: Consistent behavior across Windows, Linux, macOS
- **Performance-Optimized**: Efficient processing for real-time operations
- **Extensible**: Plugin-like architecture for future enhancements

### Module Structure
```
src/embedded_cereal_bowl/
├── __init__.py              # Package initialization and exports
├── cli.py                   # Unified command-line interface
├── archive_logs.py            # Log file management utilities
├── check_crlf.py            # Line ending validation
├── formatter/                # Code formatting module
│   ├── __init__.py
│   └── formatter.py        # Multi-tool formatting engine
├── monitor/                  # Serial communication module
│   ├── __init__.py
│   └── monitor.py          # Core serial monitor
├── timestamp/               # Time conversion module
│   ├── __init__.py
│   └── timestamp.py        # Unix/ISO time conversion
└── utils/                   # Shared utilities
    ├── __init__.py
    └── color_utils.py     # Terminal color management
```

---

## 🔌 Serial Monitor Architecture

### Thread-Based Design
```
┌─────────────────────────────────────────────────────────────────┐
│                    Main Thread                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌───────────────────────────────────┐  │
│  │ Serial Read  │  │       Input Handler Thread        │  │
│  │   Thread     │  │  (if --send enabled)           │  │
│  └─────────────┘  │  ┌─────────┐  ┌──────────────┐  │
│                 │  │ User    │  │ Command      │  │
│                 │  │ Input   │  │ Processing   │  │
│                 │  │ Thread  │  │ Thread       │  │
│                 │  └─────────┘  └──────────────┘  │
│                 └───────────────────────────────────────────┘
│                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Logging Thread                   │   │
│  │  (if --log enabled)                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture
```
Serial Port → Read Buffer → Parser → Processor → Output
     ↑                                            ↓
User Input ← Input Handler ← Command Queue ← Send Thread
     ↑                                            ↓
     File ← Logger ← Timestamp ← Processed Data
```

### State Management
```python
class SerialMonitorState:
    connection_state: ConnectionStatus
    file_handle: Optional[TextIO]
    highlight_words: List[str]
    timestamp_mode: TimestampMode
    send_enabled: bool
    logging_enabled: bool
    
    def transition_to(self, new_state: ConnectionStatus):
        # State transition logic with validation
```

---

## ✨ Code Formatter Architecture

### Parallel Processing Design
```python
class ParallelFormatter:
    def __init__(self, max_jobs: int = None):
        self.max_jobs = min(max_jobs, os.cpu_count())
        self.executor = ThreadPoolExecutor(max_workers=self.max_jobs)
    
    def format_directory(self, root_dir: Path):
        # Discover files -> Partition -> Process -> Aggregate results
        file_batches = self._partition_files(files)
        futures = self._submit_batches(file_batches)
        return self._aggregate_results(futures)
```

### Tool Detection and Execution
```python
class ToolRegistry:
    tools = {
        '.c': ClangFormatTool(),
        '.cpp': ClangFormatTool(), 
        '.cmake': CMakeFormatTool(),
    }
    
    def get_tool(self, file_path: Path) -> FormatTool:
        extension = file_path.suffix.lower()
        return self.tools.get(extension)
```

### Extensibility Framework
```python
class FormatTool(ABC):
    @abstractmethod
    def check_available(self) -> bool: pass
    
    @abstractmethod
    def format_file(self, file_path: Path, check_only: bool) -> bool: pass
    
    @abstractmethod  
    def get_file_extensions(self) -> List[str]: pass
```

---

## 🗓️ Timestamp Converter Architecture

### Format Detection Engine
```python
class TimestampDetector:
    def detect_format(self, input_str: str) -> TimestampFormat:
        # Pattern matching for various formats
        if self._is_unix_timestamp(input_str):
            return TimestampFormat.UNIX_SECONDS
        elif self._is_milliseconds_timestamp(input_str):
            return TimestampFormat.UNIX_MILLISECONDS
        elif self._is_iso8601(input_str):
            return TimestampFormat.ISO8601
```

### Conversion Pipeline
```
Input String → Format Detection → Parsing → Validation → Conversion → Output
     ↓                                    ↓           ↓          ↓
   Pattern Regex → Date/Time Parse → Range Check → UTC/Local → Formatted String
```

### Timezone Handling
```python
class TimezoneHandler:
    def get_local_timezone(self) -> tzinfo:
        # System timezone detection with fallbacks
        
    def convert_to_local(self, utc_datetime: datetime) -> datetime:
        # DST-aware local conversion
        
    def format_local_offset(self, local_dt: datetime) -> str:
        # Human-readable offset formatting
```

---

## ⚠️ CRLF Checker Architecture

### File Classification System
```python
class FileClassifier:
    BINARY_EXTENSIONS = {'.jpg', '.png', '.zip', '.exe'}
    TEXT_PATTERNS = {r'\.txt$', r'\.py$', r'\.c$'}
    
    def classify_file(self, file_path: Path) -> FileType:
        if self._is_binary(file_path):
            return FileType.BINARY
        return FileType.TEXT
```

### Line Ending Detection
```python
class LineEndingDetector:
    def detect(self, file_path: Path) -> LineEndingType:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)  # Read first 8KB
            if b'\r\n' in chunk:
                return LineEndingType.CRLF
            elif b'\n' in chunk:
                return LineEndingType.LF
        return LineEndingType.UNKNOWN
```

---

## 🎨 Color and Terminal Architecture

### Cross-Platform Color System
```python
class ColorManager:
    def __init__(self):
        self.colors_enabled = self._detect_color_support()
        self.color_palette = self._load_color_palette()
    
    def colorize(self, text: str, color: Color) -> str:
        if not self.colors_enabled:
            return text
        return self._apply_ansi_codes(text, color)
```

### ANSI Code Management
```python
class ANSICodeHandler:
    @staticmethod
    def strip_ansi_codes(text: str) -> str:
        # Remove ANSI escape sequences for logging
        
    @staticmethod
    def extract_ansi_codes(text: str) -> List[str]:
        # Extract color codes for state preservation
```

---

## 🔧 Configuration System

### Configuration Hierarchy
```
1. Command Line Arguments (highest priority)
2. Environment Variables  
3. Configuration Files
   a. ~/.config/embedded-cereal-bowl/config.json
   b. ./embedded-cereal-bowl.json
   c. /etc/embedded-cereal-bowl/config.json
4. Default Values (lowest priority)
```

### Configuration Schema
```json
{
  "serial_monitor": {
    "default_baud_rate": 115200,
    "default_timeout": 5.0,
    "highlight_colors": {
      "error": "red",
      "warning": "yellow",
      "info": "blue"
    }
  },
  "formatter": {
    "default_jobs": "auto",
    "ignore_patterns": [".git", "build", "__pycache__"]
  },
  "timestamp": {
    "default_output_format": "both",
    "timezone": "auto"
  }
}
```

---

## 🚀 Performance Optimizations

### Memory Management
- **Object Pooling**: Reuse objects for high-frequency operations
- **Stream Processing**: Process data in chunks to minimize memory usage
- **Lazy Loading**: Load modules only when needed

### CPU Optimization  
- **Parallel Processing**: Multi-threading for I/O and CPU-bound tasks
- **Smart Caching**: Cache expensive computations and system queries
- **Event-Driven**: Use event loops instead of polling where possible

### I/O Optimization
- **Buffered I/O**: Use appropriate buffer sizes for file operations
- **Asynchronous Operations**: Non-blocking I/O for responsiveness
- **Batch Processing**: Group similar operations to reduce system calls

---

## 🧪 Testing Architecture

### Test Categories
```
Unit Tests
├── timestamp conversion logic
├── line ending detection
├── color utility functions
└── configuration parsing

Integration Tests  
├── serial port communication (mocked)
├── file system operations
├── CLI command execution
└── tool integration workflows

Performance Tests
├── large file processing
├── high-frequency operations
├── memory usage validation
└── concurrent operations
```

### Mocking Strategy
```python
class MockSerialPort:
    def __init__(self, test_data: List[str]):
        self.test_data = test_data
        self.write_buffer = []
        
    def read(self, size: int) -> bytes:
        # Simulate serial data reception
        return self.test_data.pop(0).encode()
        
    def write(self, data: bytes) -> int:
        # Capture sent data for validation
        self.write_buffer.append(data.decode())
        return len(data)
```

---

## 🔄 Extension Points

### Plugin Architecture
```python
class ToolPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass
    
    @abstractmethod
    def execute(self, args: List[str]) -> int: pass
    
    @abstractmethod
    def get_help(self) -> str: pass
```

### Future Extensibility
- **New Serial Protocols**: Add support for MODBUS, CAN bus, SPI
- **Additional Formatters**: Support for black, prettier, rustfmt
- **Database Integration**: Log to SQLite, PostgreSQL, InfluxDB
- **Web Interface**: Real-time web-based monitoring dashboard

---

## 🛡️ Security Architecture

### Input Validation
```python
class InputValidator:
    @staticmethod
    def validate_port_path(port: str) -> bool:
        # Validate port path format and permissions
        
    @staticmethod  
    def validate_baud_rate(baud: int) -> bool:
        # Check standard baud rates and ranges
```

### Sandboxing
- **Process Isolation**: Run external tools in controlled environments
- **Resource Limits**: Impose CPU and memory limits
- **Path Validation**: Prevent path traversal attacks

This architecture enables maintainable, extensible, and performant embedded development tools.