#! /usr/bin/env python3

import serial
import sys
import os
import argparse
import datetime
import regex as re
import time

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=str, default="ACM0",
                        help="Specify the serial port to connect to, eg ACM0, USB0, COM3")
    parser.add_argument("-b", "--baud", type=int, default=2000000,
                        help="Baud rate to set the serial port to")
    parser.add_argument("-l", "--log", action="store_true",
                        help="save serial port data to log file")
    parser.add_argument("-lf", "--log-file", type=str, default="log",
                        help="filename used to save log files. Will appear as date_time_<filename>.txt")
    parser.add_argument("-ld", "--log-directory", type=str,
                        help="Folder to save logging file. Default is script directory")
    parser.add_argument("-c", "--clear", action="store_true",
                        help="Clear terminal before printing")
    parser.add_argument("-t", "--print_time", action="store_true",
                        help="print system time on each log line")

    return parser.parse_args()


def print_and_quit(str):
    print(str)
    sys.exit(1)

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def run_serial_printing_with_logs(serial_port_name, baud, print_time, log_file, log_directory):
    filename = "{}_{}.txt".format(
        (datetime.datetime.now()).strftime("%Y.%m.%d_%H.%M.%S"), log_file)
    if log_directory:
        logging_file = "{}/{}".format(log_directory, filename)
    else:
        script_location = os.path.dirname(os.path.realpath(__file__))
        logging_file = "{}/{}".format(script_location, filename)
    print("Logging to: {}".format(logging_file))

    with open(logging_file, 'a+') as file:
        run_serial_printing(serial_port_name, baud, file, print_time)


def run_serial_printing(serial_port_name, baud, print_time, file=None):
    today = int(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%s'))
    with serial.Serial(serial_port_name, baud, timeout=0.01) as ser:
        print("----------------------------------------")
        while True:
            try:
                line = ser.readline()
                decoded_line = line.decode('utf-8', errors="ignore")

                if (len(decoded_line) > 0):
                    if print_time:
                        print("{:.3f} ".format(time.time() - today), end='')
                    print(decoded_line, end='')

                if file:
                    colours_stripped = escape_ansi(decoded_line)
                    file.write(colours_stripped)
            except serial.SerialException:
                print_and_quit("Monitor: Disconnected (Serial exception)")
            except IOError:
                print_and_quit("Monitor: Disconnected (I/O Error)")
            except KeyboardInterrupt:
                print_and_quit("Monitor: Keyboard Interrupt. Exiting Now...")


def main():
    args = parse_arguments()
    print(args)

    # clear screen
    if os.name == 'nt':
        if args.clear:
            os.system('cls')
        serial_prefix = ""
    else:
        if args.clear:
            os.system('clear')
        serial_prefix = "/dev/tty"

    serial_port_name = "{}{}".format(serial_prefix, args.port)
    print("This session: Port: {} {}".format(serial_port_name, args.baud))
    
    if args.log == True:
        run_serial_printing_with_logs(serial_port_name, args.baud, args.print_time, args.log_file, args.log_directory)
    else:
        run_serial_printing(serial_port_name, args.baud, args.print_time)


if (__name__ == '__main__'):
    main()
