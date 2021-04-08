#! /usr/bin/env python3

import serial
import sys
import time
import os
from datetime import datetime
import string

# clear screen
os.system('cls' if os.name == 'nt' else 'clear')

baud = 2000000
port = "ACM0"

# make sure config file is loaded from script dir rather than cwd
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
config_file_full_path = os.path.join(__location__,"config.txt")

if(len(sys.argv) >= 2):
    port = str(sys.argv[1])
    if(len(sys.argv) == 3):
        baud = sys.argv[2]
    else:
        print("Baud not specified, using default")
else:
    try:
        with open(config_file_full_path, "r") as config_file:
            port = config_file.readline().strip()
            baud = config_file.readline().strip()
    except:
        print("No config file or args. Using default")
        pass

print("This session: Port: /dev/tty" + port + " Baud: " + str(baud))
print("------------------------------------------------")

serial_prefix = "/dev/tty"
if os.name == 'nt':
    serial_prefix = ""

def main():
    with serial.Serial(serial_prefix + port, baud, timeout=1) as ser:
        ser.flush()
        while True:
            try:
                line = ser.readline()
                decoded_line = line.decode('utf-8', errors="ignore")
                print(decoded_line, end='')
            except serial.SerialException:
                print("Monitor: Disconnected (Serial exception)")
                sys.exit(1)
            except IOError:
                print("Monitor: Disconnected (I/O Error)")
                sys.exit(1)
            except KeyboardInterrupt:
                print("Monitor: Keyboard Interrupt. Exiting Now...")
                sys.exit(1)

if (__name__ == '__main__'): 
    main()
