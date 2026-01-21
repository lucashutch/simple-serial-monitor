# ⚠️ CRLF Line Ending Checker

Scan directories for files with incorrect CRLF (\\r\\n) line endings instead of standard LF (\\n) for cross-platform compatibility.

## 🚀 Quick Start

```bash
# Check current directory
check-crlf

# Check specific directory  
check-crlf /path/to/project

# Ignore specific directories
check-crlf --ignore build third-party .git

# Verbose output
check-crlf --verbose
```

## 📖 File Types Checked

### Binary Files (Skipped)
- Images: `.jpg`, `.png`, `.gif`, `.bmp`, `.svg`
- Archives: `.zip`, `.tar`, `.gz`, `.rar`
- Compiled: `.exe`, `.dll`, `.so`, `.dylib`
- Documents: `.pdf`, `.doc`, `.xls`

### Text Files (Scanned)
| Extension | Type | Notes |
|---|---|---|
| `.py` | Python | Source code |
| `.c`, `.cpp`, `.h` | C/C++ | Source code |
| `.cmake` | CMake | Build scripts |
| `.txt`, `.md` | Documentation | Text files |
| `.sh`, `.bat` | Scripts | Shell scripts |
| `.yml`, `.yaml` | Configuration | YAML files |
| `.json` | Data | JSON files |
| `.xml` | Data | XML files |

## 🔧 Command Reference

```bash
usage: check_crlf.py [-h] [--ignore DIR [DIR ...]] [-v] [root_dir]
```

### Options
| Option | Short | Long | Description | Example |
|---|---|---|---|
| Ignore | `--ignore` | Skip directories | `--ignore build third-party` |
| Verbose | `-v` | `--verbose` | Detailed output | `--verbose` |
| Help | `-h` | `--help` | Show help | `-h` |

## 📊 Output Examples

### Normal Mode
```bash
$ check-crlf
✓ All files have correct line endings
```

### Files with CRLF Found
```bash
$ check-crlf --verbose
Scanning: /home/user/project/
✗ File has CRLF endings: src/main.c
✗ File has CRLF endings: include/header.h
✗ File has CRLF endings: README.md

Found 3 files with CRLF line endings
```

### Detailed Verbose Output
```bash
$ check-crlf --verbose
Scanning: /path/to/project/
Checking: src/main.c (C/C++ source)
  Line endings: CRLF detected
  Size: 1024 bytes, 42 lines
Checking: include/utils.h (C/C++ source)  
  Line endings: CRLF detected
  Size: 512 bytes, 18 lines
Checking: README.md (Documentation)
  Line endings: CRLF detected  
  Size: 2048 bytes, 85 lines

Summary:
  Files checked: 156
  Files with CRLF: 3
  Files with LF: 153
```

### With Ignore Directories
```bash
$ check-crlf --ignore build third-party .git --verbose
Scanning: /path/to/project/
Ignoring: build/
Ignoring: third_party/
Ignoring: .git/
Checking: src/main.c
  Line endings: LF (correct)
```

## 🎯 Common Use Cases

### Git Repository Cleanup
```bash
# Check entire repository
check-crlf --ignore .git

# Before committing
git add .
check-crlf
if [ $? -ne 0 ]; then
  echo "Fix line endings before committing"
  exit 1
fi
```

### Cross-Platform Projects
```bash
# Project shared between Windows and Linux/macOS
check-crlf --ignore build output

# Automated checking in CI
check-crlf --verbose --ignore .git build/
```

### Open Source Contributions
```bash
# Before pull request
check-crlf --ignore .git

# Check specific changed files
git diff --name-only HEAD~1 | xargs check-crlf
```

## 💡 Integration Examples

### Git Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Checking line endings..."
check-crlf --ignore .git
if [ $? -ne 0 ]; then
  echo "Files have incorrect line endings. Use dos2unix or similar tools."
  echo "Run: find . -type f -not -path './.git/*' -exec dos2unix {} \\;"
  exit 1
fi
```

### Makefile Integration
```makefile
# Makefile
check-line-endings:
	check-crlf --ignore .git build/

fix-line-endings:
	find . -type f -not -path './.git/*' -not -path './build/*' -exec dos2unix {} \;

.PHONY: check-line-endings fix-line-endings
```

### CI/CD Pipeline
```bash
# .github/workflows/ci.yml
- name: Check line endings
  run: |
    check-crlf --ignore .git build/
    if [ $? -ne 0 ]; then
      echo "Line ending check failed"
      exit 1
    fi
```

## 🔧 Fixing CRLF Issues

### Using dos2unix
```bash
# Install dos2unix
# Ubuntu/Debian: sudo apt install dos2unix
# macOS: brew install dos2unix
# Windows: included with Git Bash

# Fix all files
find . -type f -not -path './.git/*' -exec dos2unix {} \;

# Fix specific files
dos2unix src/main.c include/header.h
```

### Using sed
```bash
# Convert CRLF to LF (Unix/Linux/macOS)
find . -type f -exec sed -i 's/\r$//' {} \;

# Convert LF to CRLF (Windows)
find . -type f -exec sed -i 's/$/\r/' {} \;
```

### Git Configuration
```bash
# Git autocrlf settings
git config --global core.autocrlf input   # Convert CRLF to LF on commit
git config --global core.autocrlf true    # Convert between platforms
git config --global core.eol lf          # Force LF in repository
```

### Editor Configuration
```bash
# VS Code (.vscode/settings.json)
{
  "files.eol": "\\n",
  "files.insertFinalNewline": true
}

# Vim (.vimrc)
set fileformat=unix
set fileformats=unix,dos
```

## 🚀 Performance Tips

### Large Projects
```bash
# Ignore binary-heavy directories
check-crlf --ignore .git node_modules dist build

# Use verbose for progress tracking
check-crlf --verbose

# Check specific subdirectory
check-crlf src/ --ignore build/
```

### Optimization
```bash
# File type detection optimization
check-crlf --ignore "*.exe" "*.dll" "*.so"

# Directory-specific checking
check-crlf src/ include/ --ignore build/
```

## ⚠️ Troubleshooting

### Permission Issues
```bash
# Make script executable
chmod +x check-crlf

# Check file permissions
ls -la check-crlf
```

### Binary File Detection
```bash
# Script correctly identifies binary files
file src/main.c        # Should show text/C source
file image.jpg        # Should show image data
```

### Performance Issues
```bash
# Optimize for large repositories
check-crlf --ignore .git node_modules build/ dist/

# Use specific directory targeting
check-crlf src/ include/ tests/
```

### False Positives
```bash
# If text files are incorrectly identified as binary:
# Script checks for NULL bytes and known binary signatures
# Override by checking specific file:
check-crlf path/to/specific-file.txt
```

## 🔍 Advanced Configuration

### Custom File Type Detection
The checker uses multiple heuristics:
1. **File extension** mapping to known types
2. **NULL byte** detection in content
3. **Binary signatures** (ELF, PE, Mach-O, etc.)
4. **MIME type** checking (if available)

### Performance Characteristics
| Project Size | Scan Time | Memory Usage |
|---|---|---|
| Small (< 100 files) | < 1 second | < 10 MB |
| Medium (100-1000 files) | 1-5 seconds | 10-50 MB |
| Large (> 1000 files) | 5-30 seconds | 50-200 MB |

For more examples, see [Examples Directory](examples/).