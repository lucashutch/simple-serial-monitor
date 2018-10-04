#! /usr/bin/env python3

import serial
import sys
import time
import os
from datetime import datetime

baud = 2000000
os.system('cls' if os.name == 'nt' else 'clear')

print("--------------Simple Serial Monitor-------------")

if(len(sys.argv) > 3 or len(sys.argv) < 2):
    print("Incorrect arguments. run with -h to see options")
    sys.exit(1)

if(len(sys.argv) == 3):
    baud = sys.argv[2]

if str(sys.argv[1]) == "-h":
    print("Useage:  * Arg_1: Port  * Arg_2: Baud           ")
    print("         * ctrl+c to quit                       ")
    print("------------------------------------------------")
    sys.exit(1)

print("This session: Port: /dev/tty" + str(sys.argv[1]) + " Baud: " + str(baud))
print("------------------------------------------------")

with serial.Serial("/dev/tty" + sys.argv[1], baud, timeout=1) as ser:
    while True:
        try:
            time.sleep(0.05)
            bytesToRead = ser.inWaiting() # get the amount of bytes available at the input queue
            if bytesToRead:
                line = ser.read(ser.inWaiting())
                print(line.decode('utf-8'), end="")
                # print(line.strip().decode('utf-8'))
        except UnicodeDecodeError:
            thing =1
            # dont do anything..
        except serial.SerialException:
            print("Monitor: Disconnected (Serial exception)")
            sys.exit(1)
        except IOError:
            print("Monitor: Disconnected (I/O Error)")
            sys.exit(1)
        except KeyboardInterrupt:
            print("Monitor: Keyboard Interrupt. Exiting Now...")
            sys.exit(1)
