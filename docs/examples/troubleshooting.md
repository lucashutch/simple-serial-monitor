# 🐛 Troubleshooting Guide

Common issues and solutions for Embedded Cereal Bowl tools and embedded development scenarios.

## 📋 Issues Index

### 🔌 Connection Issues
- [Permission Denied](#permission-denied) - Serial port access problems
- [Port Not Found](#port-not-found) - Device detection issues
- [Connection Timeout](#connection-timeout) - Communication problems
- [Auto-Reconnect Issues](#auto-reconnect-issues) - Reconnection failures



### 🔧 Tool Issues
- [Installation Problems](#installation-problems) - Setup and installation issues
- [Command Not Found](#command-not-found) - Scripts not executable
- [Configuration Issues](#configuration-issues) - Settings and setup problems

---

## 🔌 Permission Denied

### Linux/macOS
```bash
# Check current user groups
groups $USER

# Add user to dialout group (for serial access)
sudo usermod -a -G dialout $USER

# Alternative: Add specific user to uucp group
sudo usermod -a -G uucp $USER

# Apply changes (requires logout/login)
newgrp dialout
# OR fully logout and log in again
```

### Ubuntu/Debian Specific
```bash
# Check serial port permissions
ls -la /dev/ttyACM* /dev/ttyUSB*

# Fix permissions temporarily
sudo chmod 666 /dev/ttyACM0

# Permanent fix via udev rules
sudo nano /etc/udev/rules.d/99-serial-ports.rules
# Add: KERNEL=="ttyACM*", MODE="0666", GROUP="dialout"
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Windows
```bash
# Run as Administrator
# Right-click PowerShell/CMD -> "Run as administrator"

# Check port permissions in Device Manager
# Devmgmt.msc -> Ports (COM & LPT) -> Properties
```

---

## 🔌 Port Not Found

### Port Detection Commands
```bash
# Linux: List all serial ports
ls /dev/tty*
dmesg | grep -i tty

# macOS: List USB and modem devices
ls /dev/tty.usb*
ls /dev/cu.usb*

# Windows: Check Device Manager or PowerShell
# PowerShell:
Get-WMIObject Win32_SerialPort
# Device Manager -> Ports (COM & LPT)
```

### Common Port Names
| Platform | Arduino | ESP32 | USB-Serial | Generic |
|---|---|---|---|---|
| Linux | `ttyACM*` | `ttyUSB*` | `ttyUSB*` | `ttyS*` |
| macOS | `cu.usbmodem*` | `cu.usbserial*` | `cu.usbserial*` | `cu.usbmodem*` |
| Windows | `COM3-5` | `COM3-10` | `COM1-4` | `COM1-20` |

### Debugging Port Detection
```bash
# Test with different baud rates
monitor --port ACM0 --baud 9600
monitor --port ACM0 --baud 38400  
monitor --port ACM0 --baud 115200

# Check with verbose output
monitor --verbose --port ACM0
```

---

## 🔌 Connection Timeout

### Timeout Configuration
```bash
# Increase timeout values (if configurable)
monitor --timeout 30 --port ACM0

# Retry connection attempts
monitor --retry 3 --port ACM0

# Use lower baud rate for stability
monitor --port ACM0 --baud 9600
```

### Hardware Solutions
```bash
# Check USB cable connection
lsusb | grep -i serial

# Test with different USB port
monitor --port ACM1  # Try ACM1 instead of ACM0

# Check device power
dmesg | tail -20  # Recent kernel messages
```

### Software Solutions
```bash
# Clear port (may be locked)
sudo fuser -k /dev/ttyACM0  # Kill processes using port

# Reset USB subsystem (Linux)
sudo usbreset /dev/bus/usb/001/001  # Reset USB device

# Wait and retry
sleep 2 && monitor --port ACM0
```

---

## 🔌 Auto-Reconnect Issues

### Disable Auto-Reconnect
```bash
# Manual mode for debugging
monitor --no-reconnect --port ACM0

# Increase retry intervals
monitor --retry-delay 10 --port ACM0
```

### Custom Reconnect Logic
```bash
# Exponential backoff
while true; do
    monitor --port ACM0 --timeout 10
    sleep $((2**counter))
    counter=$((counter+1))
done
```

### Advanced Reconnection
```bash
# Health check before reconnect
monitor --health-check --port ACM0

# Reconnect with different configuration
monitor --port ACM0 --baud-backup 9600 --reconnect-timeout 30
```



### Optimization Strategies
```bash
# Reduce highlight processing
monitor --highlight=error,warning  # Fewer keywords to process

# Disable unnecessary features
monitor --no-timestamp --no-colors

# Lower refresh rate
monitor --refresh-delay 100  # milliseconds
```

### Hardware Solutions
```bash
# Use faster USB port
monitor --port USB0  # USB 3.0 instead of USB 2.0

# Optimize system resources
nice -n 10 monitor  # Lower priority
```

---

## 📝 Memory Leaks

### Monitor Memory Usage
```bash
# Real-time memory monitoring
watch -n 1 'ps aux | grep monitor'

# Detailed memory analysis
valgrind --tool=memcheck monitor --port ACM0

# System memory overview
free -h
cat /proc/meminfo
```

### Leak Detection
```bash
# Long-running test
timeout 3600 monitor --log --port ACM0

# Check memory growth over time
while true; do
    ps aux | grep monitor | awk '{print $6}'
    sleep 60
done
```

### Optimization
```bash
# Limit log file size
monitor --log --max-size 100MB --rotate-logs

# Disable features not needed
monitor --no-colors --no-highlight
```

---



### Optimization
```bash
# Increase buffer sizes
monitor --buffer-size 8192

# Use binary mode for speed
monitor --binary --port ACM0

# Parallel processing
monitor --parallel-threads 4
```

---

## 🔧 Installation Problems

### Python Issues
```bash
# Check Python version
python3 --version  # Should be 3.12+

# Check pip version
pip --version

# Force specific Python version
python3.12 -m pip install embedded-cereal-bowl
```

### Permission Issues
```bash
# User installation without sudo
pip install --user embedded-cereal-bowl

# Fix PATH for user installs
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Dependency Issues
```bash
# Install specific dependencies
pip install pyserial==3.5
pip install regex==2022.0.0

# Force reinstall broken package
pip uninstall pyserial && pip install pyserial
```

### Virtual Environment Issues
```bash
# Clean environment recreation
python3 -m venv new_env
source new_env/bin/activate
pip install embedded-cereal-bowl
```

---

## 🔧 Command Not Found

### Check Installation
```bash
# Verify package installation
python -c "import embedded_cereal_bowl; print('OK')"

# Check script paths
which monitor
which timestamp
which check-crlf
which format-code
```

### Fix Path Issues
```bash
# Add to PATH (temporary)
export PATH="$HOME/.local/bin:$PATH"

# Add to PATH (permanent)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Create symlinks
sudo ln -s ~/.local/bin/monitor /usr/local/bin/monitor
```

### Make Scripts Executable
```bash
# Fix script permissions
chmod +x ~/.local/bin/monitor
chmod +x ~/.local/bin/timestamp
chmod +x ~/.local/bin/check-crlf
chmod +x ~/.local/bin/format-code
```

---

## 🔧 Configuration Issues

### Check Configuration Files
```bash
# Find configuration files
find ~ -name "*.conf" -o -name "*.config" -o -name "*.ini"

# Check default config locations
ls ~/.config/embedded-cereal-bowl/
ls /etc/embedded-cereal-bowl/
```

### Reset Configuration
```bash
# Remove user configuration
rm -rf ~/.config/embedded-cereal-bowl/

# Use defaults only
monitor --reset-config --port ACM0

# Create fresh configuration
monitor --init-config --port ACM0 --baud 115200
```

### Environment Variables
```bash
# Check relevant environment
env | grep -i serial
env | grep -i monitor
env | grep -i python

# Clear problematic variables
unset EMBEDDED_MONITOR_CONFIG
export EMBEDDED_MONITOR_DEBUG=1
```



## 📞 Getting Help

### Collect Debug Information
```bash
# System information gathering
uname -a > debug_info.txt
python --version >> debug_info.txt
pip list >> debug_info.txt
ls -la /dev/tty* >> debug_info.txt
```

### Report Issues Effectively
```markdown
Issue Report Template:
```
## Environment
- OS: [Linux/macOS/Windows] [Version]
- Python: [3.12.x]
- Package: [0.1.x]

## Problem
- Command: [monitor --port ACM0 --send]
- Error: [Permission denied]
- Expected: [Should connect to Arduino]

## Troubleshooting Steps
1. [Checked user groups - in dialout]
2. [Tried different port - ACM1]
3. [Tried as root - works]

## Additional Info
- Hardware: [Arduino Uno R3]
- USB cable: [Original/Aftermarket]
- Other software: [None running]
```

### Community Resources
- [GitHub Issues](https://github.com/lucashutch/embedded-cereal-bowl/issues)
- [Discussions](https://github.com/lucashutch/embedded-cereal-bowl/discussions)
- [Wiki](https://github.com/lucashutch/embedded-cereal-bowl/wiki)

Remember to check the [Examples Directory](embedded-projects.md) for working configurations and [Installation Guide](installation.md) for setup issues.