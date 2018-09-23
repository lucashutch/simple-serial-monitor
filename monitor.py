#! /usr/bin/env python3

import serial
import sys
import time
from datetime import datetime


print("--------------Simple Serial Monitor-------------")

if str(sys.argv[1]) == "-h":
    print("Useage:  * Arg_1: Port  * Arg_2: Baud           ")
    print("         * ctrl+c to quit                       ")
    print("------------------------------------------------")
    sys.exit(1)

print("This session: Port: " + str(sys.argv[1]) + " Baud: " + str(sys.argv[2]))
print("------------------------------------------------")

with serial.Serial(sys.argv[1], sys.argv[2], timeout=1) as ser:
    while True:
        try:
            time.sleep(0.05)
            bytesToRead = ser.inWaiting() # get the amount of bytes available at the input queue
            if bytesToRead:
                line = ser.read(ser.inWaiting())
                # print(datetime.utcnow().strftime("(%H:%M:%S.%f) - ")[:-3])
                print(line.strip().decode('utf-8'), end="")
        except UnicodeDecodeError:
            print("coulnd't decode character")
        except serial.SerialException:
            print("Monitor: Disconnected (Serial exception)")
            sys.exit(1)
        except IOError:
            print("Monitor: Disconnected (I/O Error)")
            sys.exit(1)
        except KeyboardInterrupt:
            print("Monitor: Keyboard Interrupt. Exiting Now...")
            sys.exit(1)
