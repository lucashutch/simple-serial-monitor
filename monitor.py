#! /usr/bin/env python3

import serial
import sys
import os
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=str, default="ACM0",
                        help="Specify the serial port to connect to, eg ACM0, USB0, COM3")
    parser.add_argument("-b", "--baud", type=int, default=2000000,
                        help="Baud rate to set the serial port to")
    return parser.parse_args()

def run_main_loop(port, baud):
    # clear screen
    if os.name == 'nt':
        os.system('cls')
        serial_prefix = ""
    else:
        os.system('clear')
        serial_prefix = "/dev/tty"

    print("This session: Port: {}{} {}".format(serial_prefix, port, baud))
    print("----------------------------------------")
        
    with serial.Serial(serial_prefix + port, baud, timeout=0.01) as ser:
        while True:
            try:
                decoded_line = ser.readline().decode('utf-8', errors="ignore")
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

def main():
    args = parse_arguments()
    print(args)
    run_main_loop(args.port, args.baud)
    

if (__name__ == '__main__'): 
    main()
