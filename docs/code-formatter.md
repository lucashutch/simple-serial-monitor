# ✨ Code Formatter

Universal code formatting tool supporting multiple file types and external formatting tools with parallel processing.

## 🚀 Quick Start

```bash
# Format current directory
format-code

# Check formatting without changes
format-code --check

# Format specific directory
format-code /path/to/project

# Parallel processing with 4 jobs
format-code --jobs 4
```

## 📖 Supported Tools

| Tool | File Extensions | File Patterns | Notes |
|---|---|---|---|
| **clang-format** | `.h`, `.hpp`, `.hxx`, `.hh`, `.c`, `.cpp`, `.cxx`, `.cc` | Header and source files |
| **cmake-format** | `.cmake` | `CMakeLists.txt` |

### Installation Requirements
```bash
# Ubuntu/Debian
sudo apt install clang-format cmake-format

# macOS (with Homebrew)
brew install clang-format cmake-format

# Windows (with Chocolatey)
choco install clang-format cmake-format

# Verify installation
clang-format --version
cmake-format --version
```

## 🔧 Full Command Reference

```bash
usage: formatter.py [-h] [-i DIR [DIR ...]] [-j JOBS] [-v] [--check] [root_dir]
```

### Options Details

| Option | Short | Long | Description | Example |
|---|---|---|---|
| Ignore Directories | `-i` | `--ignore` | Skip directories | `--ignore build third-party` |
| Jobs | `-j` | `--jobs` | Parallel jobs | `--jobs 4` |
| Verbose | `-v` | `--verbose` | Detailed output | `--verbose` |
| Check Only | `--check` | `-c` | Check without changes | `--check` |
| Help | `-h` | `--help` | Show help | `-h` |

## 🎯 Usage Patterns

### Basic Formatting
```bash
# Format current directory recursively
format-code

# Format with all CPU cores
format-code --jobs $(nproc)

# Verbose output
format-code --verbose
```

### Check Mode
```bash
# Check what needs formatting
format-code --check

# CI/CD integration
format-code --check --verbose
```

### Project-Specific Formatting
```bash
# Embedded C++ project
format-code /path/to/embedded/project

# With common ignores
format-code --ignore build third-party .git output
```

### Parallel Processing
```bash
# 4 parallel jobs
format-code --jobs 4

# Use 75% of CPU cores
format-code --jobs $(($(nproc) * 3 / 4))
```

## 📁 Directory Structure Handling

### Typical Project Layout
```
project/
├── src/
│   ├── main.c
│   ├── utils.cpp
│   └── include/
│       └── header.h
├── CMakeLists.txt
├── build/           # ignored by default
├── third_party/     # commonly ignored
└── external/        # commonly ignored
```

### Smart File Discovery
The formatter:
- Scans recursively from root directory
- Matches files by extension only
- Respects ignore patterns
- Processes files in parallel

## 📊 Output Examples

### Normal Formatting
```bash
$ format-code --verbose
Found 12 files to format
Processing with 4 parallel jobs...
Formatted: src/main.c
Formatted: include/header.h
Formatted: CMakeLists.txt
✓ All files formatted successfully
```

### Check Mode
```bash
$ format-code --check --verbose
Found 12 files to check
Processing with 4 parallel jobs...
✗ src/main.c requires formatting
✗ include/utils.h requires formatting
Files requiring changes: 2
Use --fix to apply changes
```

### Error Handling
```bash
$ format-code --ignore build third_party
Warning: clang-format not found in PATH
Skipping .c files (clang-format missing)
Processing: CMakeLists.txt (cmake-format available)
```

## 💡 Integration Examples

### CI/CD Pipeline
```bash
# .github/workflows/ci.yml
- name: Check code formatting
  run: |
    format-code --check
    if [ $? -ne 0 ]; then
      echo "Code formatting check failed"
      exit 1
    fi
```

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Checking code formatting..."
format-code --check
if [ $? -ne 0 ]; then
    echo "Fix formatting before committing"
    exit 1
fi
```

### Makefile Integration
```makefile
# Makefile
format:
	format-code --verbose

format-check:
	format-code --check

.PHONY: format format-check
```

## 🔧 Configuration

### clang-format Configuration
Create `.clang-format` in project root:
```yaml
BasedOnStyle: Google
IndentWidth: 4
ColumnLimit: 100
```

### cmake-format Configuration
Create `.cmake-format` in project root:
```json
{
  "line_width": 80,
  "tab_size": 2,
  "max_lines_per_function": 50
}
```

## 🚀 Performance Tips

### Optimize Parallel Jobs
```bash
# Use all cores for maximum speed
format-code --jobs $(nproc)

# Conservative for shared systems
format-code --jobs $(($(nproc) / 2))
```

### Large Projects
```bash
# Process specific directories first
format-code src/ include/
format-code tests/ examples/

# Use ignore patterns for speed
format-code --ignore build/ output/ .git/ vendor/
```

## ⚠️ Troubleshooting

### Tool Not Found
```bash
# Check tool availability
which clang-format
which cmake-format

# Install missing tools
# Ubuntu/Debian
sudo apt install clang-format cmake-format
```

### Permission Issues
```bash
# Make formatter executable
chmod +x /path/to/formatter.py

# Check script permissions
ls -la format-code
```

### Performance Issues
```bash
# Reduce parallel jobs for I/O bound systems
format-code --jobs 1

# Exclude large directories
format-code --ignore build/ dist/ node_modules/
```

For more examples, see [Examples Directory](examples/).