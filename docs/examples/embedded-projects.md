# 🏭 Embedded Development Examples

Practical examples and use cases for Embedded Cereal Bowl tools in real-world embedded development scenarios.

## 📁 Examples Index

### 🎯 Quick Links
- [Arduino Development](#-arduino-development) - Monitoring and debugging Arduino projects
- [ESP32 IoT](#-esp32-iot-projects) - IoT device monitoring and logging
- [Industrial Automation](#-industrial-automation) - PLC and industrial communication
- [Automated Testing](#-automated-testing) - Test automation and validation
- [Debugging Scenarios](#-debugging-scenarios) - Common debugging workflows

---

## 🔌 Arduino Development

### Monitoring Serial Output
```bash
# Monitor Arduino Uno/Nano (115200 baud)
monitor --port ACM0 --baud 115200 --highlight=error,warning,fail

# Monitor Arduino Mega (different baud rate)
monitor --port ACM1 --baud 9600 --log --print_time dt

# Real-time debugging with timestamps
monitor --send --highlight=debug,init,error --clear
```

### Interactive Arduino Control
```bash
# Send AT commands to Arduino modules
monitor --send --port ACM0 --baud 9600

# Common Arduino commands
> status        # Check device status
> reset         # Reset Arduino
> version       # Get firmware version
> config        # Configuration commands
```

### Arduino Project Logging
```bash
# Long-term data logging
monitor --log --print_time epoch --highlight=sensor,alarm

# Custom log naming for experiments
monitor --log-file experiment_42 --log --highlight=data,threshold
```

---

## 🌐 ESP32 IoT Projects

### ESP32 Monitoring
```bash
# Monitor ESP32 development board
monitor --port USB0 --baud 115200 --highlight=error,timeout,connect

# WiFi debugging with timestamps
monitor --port USB0 --baud 115200 --log --print_time dt --highlight=WiFi,IP,connect
```

### OTA Update Monitoring
```bash
# Monitor Over-The-Air update process
monitor --send --port USB0 --highlight=update,download,install,reboot

# Update command sequences
> start_update
> check_version
> download_firmware
> install_reboot
```

### Sensor Data Logging
```bash
# IoT sensor data collection
monitor --log --highlight=sensor,temperature,humidity,pressure

# Data validation logging
monitor --log --print_time epoch --highlight=valid,invalid,error
```

---

## 🏭 Industrial Automation

### PLC Communication
```bash
# Industrial PLC monitoring
monitor --port COM3 --baud 38400 --highlight=alarm,fault,emergency

# 24/7 monitoring with rotation logs
monitor --log --print_time dt --highlight=warning,critical,shutdown
```

### SCADA Integration
```bash
# SCADA system monitoring
monitor --send --port COM7 --baud 19200 --highlight=tag,command,response

# Command sequences for industrial control
> read_tag T101
> write_tag T201 123.45
> read_multiple T301,T302,T303
```

### Protocol Analysis
```bash
# Modbus/industrial protocol monitoring
monitor --log --highlight=register,modbus,rtu,ascii

# Timing analysis
monitor --print_time epoch --highlight=timeout,retry,crc_error
```

---

## 🧪 Automated Testing

### Production Line Testing
```bash
# Automated test sequence monitoring
monitor --send --log --print_time epoch --highlight=test,pass,fail,result

# Test command automation
monitor --send --highlight=start_test,end_test,measurement,validation
```

### Quality Assurance
```bash
# QA test monitoring
monitor --log --highlight=qa_test,defect,pass_rate,quality

# Statistical analysis logging
monitor --log --print_time dt --highlight=sample,average,deviation
```

### Continuous Integration
```bash
# CI/CD test automation
monitor --send --highlight=ci_test,build,deploy,rollback

# Integration test sequences
> start_integration
> test_connection
> validate_protocol
> end_test
```

---

## 🔍 Debugging Scenarios

### Connection Issues
```bash
# Connection debugging with verbose output
monitor --send --highlight=connect,disconnect,timeout,retry --clear

# Serial port troubleshooting
monitor --port ACM0 --baud 9600 --highlight=handshake,protocol,error
```

### Performance Analysis
```bash
# High-speed communication testing
monitor --port USB0 --baud 921600 --highlight=throughput,buffer,overflow

# Latency measurement
monitor --send --print_time epoch --highlight=latency,round_trip,timestamp
```

### Protocol Debugging
```bash
# Custom protocol monitoring
monitor --log --highlight=header,payload,checksum,sequence

# Binary protocol analysis
monitor --highlight=sync,packet,frame,crc_valid,crc_invalid
```

### Memory and Resource Debugging
```bash
# Memory leak detection
monitor --highlight=malloc,free,heap,stack,leak

# Resource monitoring
monitor --highlight=cpu_usage,memory,task_switch,deadlock
```

---

## 📊 Data Processing Examples

### Log Analysis Workflow
```bash
# 1. Collect logs with timestamps
monitor --log --print_time epoch --highlight=sensor_data > /dev/null &
PID=$!

# 2. Run test sequence
monitor --send --highlight=test_start,test_end,measurement

# 3. Stop logging and analyze
kill $PID
python analyze_logs.py logs/*.txt
```

### Automated Report Generation
```bash
# Generate daily reports
monitor --log --print_time dt --highlight=daily_report,summary,total

# Monthly trend analysis
monitor --highlight=monthly,trend,average,peak_usage
```

### Database Integration
```bash
# Real-time database logging
monitor --log --highlight=db_insert,db_error,transaction

# Data validation and cleaning
monitor --highlight=data_valid,invalid_duplicate,cleaned
```

---

## 🔧 Script Integration Examples

### Bash Script Integration
```bash
#!/bin/bash
# embedded_test.sh

echo "Starting embedded system test..."
monitor --send --port ACM0 --highlight=test,pass,fail --log

# Test sequence
echo "power_on" | socat - /dev/ttyACM0
monitor --highlight=boot_complete,ready_for_commands
```

### Python Integration
```python
#!/usr/bin/env python3
import subprocess
import time

def automated_test():
    """Automated embedded system testing."""
    # Start monitoring
    monitor_proc = subprocess.Popen([
        'monitor', '--send', '--log', '--highlight=test,pass,fail'
    ])
    
    # Send test commands
    time.sleep(2)  # Wait for connection
    with open('/dev/ttyACM0', 'w') as ser:
        ser.write(b'test_start\\n')
        time.sleep(1)
        ser.write(b'run_sequence\\n')
    
    # Monitor results
    monitor_proc.wait()

if __name__ == '__main__':
    automated_test()
```

### Makefile Integration
```makefile
# Makefile for embedded development

SERIAL_PORT = ACM0
BAUD_RATE = 115200

test: monitor
	@echo "Running embedded system test..."
	monitor --send --port $(SERIAL_PORT) --baud $(BAUD_RATE) --highlight=test,result

log: monitor
	@echo "Starting data logging..."
	monitor --port $(SERIAL_PORT) --baud $(BAUD_RATE) --log --print_time dt

debug: monitor
	@echo "Debugging mode with highlighting..."
	monitor --port $(SERIAL_PORT) --baud $(BAUD_RATE) --highlight=debug,error,warning

.PHONY: test log debug
```

---

## 🚀 Advanced Workflows

### Multi-Device Coordination
```bash
# Monitor multiple devices simultaneously
monitor --port ACM0 --highlight=device1,sync &
monitor --port ACM1 --highlight=device2,sync &
monitor --port USB0 --highlight=device3,sync &
wait

# Synchronized operations
echo "start_sync" | tee /dev/ttyACM0 /dev/ttyACM1 /dev/ttyUSB0
echo "collect_data" | tee /dev/ttyACM0 /dev/ttyACM1 /dev/ttyUSB0
```

### Automated Calibration
```bash
# Sensor calibration workflow
monitor --send --highlight=cal_start,sensor,offset,cal_end

# Calibration commands
> calibrate_zero
> read_reference
> calculate_offset
> apply_offset
> calibrate_span
> store_calibration
```

### Remote Monitoring
```bash
# SSH-based remote monitoring
ssh user@device "monitor --port /dev/ttyS0 --highlight=remote,ssh,session"

# Network-based serial monitoring
socat TCP-LISTEN:8080,fork EXEC:'monitor --port /dev/ttyUSB0' &
```

---

## ⚡ Performance Tips

### High-Speed Data Capture
```bash
# Optimize for high data rates
monitor --port USB0 --baud 921600 --log --highlight=buffer,overflow

# Reduce processing overhead
monitor --send --clear --highlight=data_only,no_processing
```

### Long-Term Reliability
```bash
# Robust monitoring setup
monitor --log --print_time epoch --highlight=reconnect,timeout,error_recovery

# Automatic restart on failure
while true; do
    monitor --send --highlight=watchdog,heartbeat
    sleep 5  # Brief pause before restart
done
```

### Data Integrity
```bash
# Checksum and validation
monitor --log --highlight=checksum,crc_valid,data_invalid

# Redundant logging
monitor --log --log-file primary.log &
monitor --log --log-file backup.log &
wait
```

## 📞 Troubleshooting Examples

See [Troubleshooting Guide](troubleshooting.md) for detailed solutions to common issues.