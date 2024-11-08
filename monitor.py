#! /usr/bin/env python3

import serial
import sys
import os
import argparse
import regex as re
import time
from datetime import datetime, timezone


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="ACM0",
        help="Specify the serial port to connect to, eg ACM0, USB0, COM3",
    )
    parser.add_argument(
        "-b",
        "--baud",
        type=int,
        default=115200,
        help="Baud rate to set the serial port to",
    )
    parser.add_argument(
        "-l", "--log", action="store_true", help="save serial port data to log file"
    )
    parser.add_argument(
        "-lf",
        "--log-file",
        type=str,
        default="log",
        help="filename used to save log files. Will appear as date_time_<filename>.txt",
    )
    parser.add_argument(
        "-ld",
        "--log-directory",
        type=str,
        help="Folder to save logging file. Default is script directory",
    )
    parser.add_argument(
        "-c", "--clear", action="store_true", help="Clear terminal before printing"
    )
    parser.add_argument(
        "-t",
        "--print_time",
        type=str,
        default="off",
        choices=["off", "epoch", "hours", "ms"],
        help="print system time on each log line",
    )
    return parser.parse_args()


def print_and_quit(str):
    print(str)
    sys.exit(1)


def escape_ansi(line):
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


def run_serial_printing_with_logs(
    serial_port_name,
    baud,
    log_file,
    log_directory,
    print_time,
):
    filename = f"{datetime.now().strftime('%Y.%m.%d_%H.%M.%S')}_{log_file}.txt"
    if log_directory:
        logging_file = f"{log_directory}/{filename}"
    else:
        script_location = os.path.dirname(os.path.realpath(__file__))
        logging_file = f"{script_location}/{filename}"
    print(f"Logging to: {logging_file}")

    with open(logging_file, "a+") as file:
        run_serial_printing(serial_port_name, baud, print_time, file)


def add_time_to_line(print_time):
    if "epoch" in print_time:
        print(f"{datetime.now(timezone.utc).timestamp():.3f} ", end="")
    elif "hours" in print_time:
        print(f"{datetime.now(timezone.utc).time()} ", end="")
    elif "ms" in print_time:
        print(f"{datetime.now(timezone.utc).timestamp() * 1000:.0f} ", end="")


def serial_loop(ser, print_time, file):
    while True:
        line = ser.readline().decode("utf-8", errors="ignore")
        if len(line) <= 0:
            continue
        add_time_to_line(print_time)
        print(line, end="")

        if file:
            file.write(escape_ansi(line))  # strip colours


def run_serial_printing(serial_port_name, baud, print_time=None, file=None):
    with serial.Serial(serial_port_name, baud, timeout=0.01) as ser:
        print("----------------------------------------")
        try:
            serial_loop(ser, print_time, file)
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
    if os.name == "nt":
        if args.clear:
            os.system("cls")
        serial_prefix = ""
    else:
        if args.clear:
            os.system("clear")
        serial_prefix = "/dev/tty"

    serial_port_name = f"{serial_prefix}{args.port}"
    print(f"This session: Port: {serial_port_name} {args.baud}")

    if args.log is True:
        run_serial_printing_with_logs(
            serial_port_name,
            args.baud,
            args.log_file,
            args.log_directory,
            args.print_time,
        )
    else:
        run_serial_printing(serial_port_name, args.baud, args.print_time)


if __name__ == "__main__":
    main()
