#! /usr/bin/env python3

import serial
import sys
import os
import argparse
import regex as re
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
        default="",
        help="filename used to save log files. Will appear as date_time_<filename>.txt",
    )
    parser.add_argument(
        "-ld",
        "--log-directory",
        type=str,
        help="Folder to save logging file. Default is script directory",
        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs"),
    )
    parser.add_argument(
        "-c", "--clear", action="store_true", help="Clear terminal before printing"
    )
    parser.add_argument(
        "-t",
        "--print_time",
        type=str,
        default="off",
        choices=["off", "epoch", "hours", "ms", "dt"],
        help="print system time on each log line",
    )
    return parser.parse_args()


def get_serial_prefix():
    if os.name == "nt":
        return ""
    else:
        return "/dev/tty"


def clear_terminal():
    # clear screen
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


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
    if not os.path.isdir(log_directory):
        os.mkdir(log_directory)

    logging_file = os.path.join(log_directory, filename)
    print(f"Logging to: {logging_file}")

    with open(logging_file, "a+", buffering=1) as file:
        run_serial_printing(serial_port_name, baud, print_time, file)


def add_time_to_line(print_time):
    if "epoch" in print_time:
        return f"{datetime.now(timezone.utc).timestamp():.3f} "
    elif "hours" in print_time:
        return f"{datetime.now(timezone.utc)}"
    elif "ms" in print_time:
        return f"{datetime.now(timezone.utc).timestamp() * 1000:.0f} "
    elif "dt" in print_time:
        return (
            f"{datetime.now(timezone.utc).date()}-{datetime.now(timezone.utc).time()} "
        )
    else:
        return ""


def serial_loop(ser, print_time, file):
    while True:
        line = ser.readline().decode("utf-8", errors="ignore")
        if len(line) <= 0:
            continue
        line = f"{add_time_to_line(print_time)}{line}"
        print(line, end="")

        if file:
            file.write(escape_ansi(line))  # strip colours


def run_serial_printing(serial_port_name, baud, print_time=None, file=None):
    serial_port_name = f"{get_serial_prefix()}{serial_port_name}"
    with serial.Serial(serial_port_name, baud, timeout=0.01) as ser:
        print("----------------------------------------")
        try:
            serial_loop(ser, print_time, file)
        except serial.SerialException:
            print(f"{os.path.basename(__file__)}: Disconnected (Serial exception)")
            sys.exit(1)
        except IOError:
            print(f"{os.path.basename(__file__)}: Disconnected (I/O Error)")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)


def main():
    args = parse_arguments()

    if args.clear:
        clear_terminal()

    print(args)

    if args.log:
        run_serial_printing_with_logs(
            args.port,
            args.baud,
            args.log_file,
            args.log_directory,
            args.print_time,
        )
    else:
        run_serial_printing(args.port, args.baud, args.print_time)


if __name__ == "__main__":
    main()
