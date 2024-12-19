# simple-serial-monitor

## Usage
```
usage: monitor.py [-h] [-p PORT] [-b BAUD] [-l] [-lf LOG_FILE] [-ld LOG_DIRECTORY] [-c] [-t]

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Specify the serial port to connect to, eg ACM0, USB0, COM3
  -b BAUD, --baud BAUD  Baud rate to set the serial port to
  -l, --log             save serial port data to log file
  -lf LOG_FILE, --log-file LOG_FILE
                        filename used to save log files. Will appear as date_time_<filename>.txt
  -ld LOG_DIRECTORY, --log-directory LOG_DIRECTORY
                        Folder to save logging file. Default is script directory
  -c, --clear           Clear terminal before printing
  -t, --print_time      print system time on each log line
  ```

## Examples
### Collect logs (/dev/ACM0 @ 115'200)
```
./monitor.py
```

### Collect logs (/dev/ACM0 @ 115'200) clearing terminal before starting
```
./monitor.py
```

### Collect logs from serial gps (/dev/ACM2 @ 9600)
```
./monitor.py -p ACM2 -b 9600
```

### Collect logs from Syrp device (/dev/ACM0 @ 2'000'000) and save to /logs/log.txt
```
./monitor.py -p ACM2 -b 2000000 -l -lf genie2 -ld /logs
```
