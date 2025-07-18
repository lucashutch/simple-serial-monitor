#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

try:
    max_width = min(os.get_terminal_size()[0], 80)
except OSError:
    max_width = 80  # Fallback to a default width if not running in a terminal


def has_crlf_endings(file_path):
    """Checks if a file has CRLF ('\r\n') line endings."""
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            if b"\r\n" not in content:
                return False
            # Ensure it's not a binary file that happens to contain the CRLF sequence.
            # This simple check for a NULL byte is a heuristic that works for most text files.
            if b"\0" in content:
                return False  # Likely a binary file, ignore it.
            return True
    except (IOError, OSError) as e:
        print(f"Error reading file: {file_path} - {e}")
    return False


def find_crlf_files(root_path, excluded_dirs=None):
    """
    Finds files with CRLF line endings in a directory, excluding specified subdirectories.
    """
    root_path = Path(root_path).resolve()
    excluded_dir_paths = set()
    if excluded_dirs:
        excluded_dir_paths = {Path(d).resolve() for d in excluded_dirs}

    crlf_files = []
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [
            d for d in dirs if (Path(root) / d).resolve() not in excluded_dir_paths
        ]

        for filename in files:
            file_path = Path(root) / filename
            if file_path.is_symlink():
                continue

            if has_crlf_endings(file_path):
                crlf_files.append(str(file_path.relative_to(root_path)))

    return crlf_files


def check_crlf_in_root(repo_path: str, ignore_dirs: list, verbose: bool = False):
    if not os.path.isdir(repo_path):
        print(f"Error: Directory not found at '{repo_path}'")
        exit(1)

    print(f"🔍 Checking for CRLF line endings in: {repo_path}")

    # Get absolute paths for reliable matching
    abs_ignore_dirs = [os.path.abspath(os.path.join(repo_path, d)) for d in ignore_dirs]

    if verbose and ignore_dirs:
        print(" Ignored Directories ".center(max_width, "-"))
        for d in abs_ignore_dirs:
            print(f"\t🚫 {d}")

    crlf_files_found = find_crlf_files(repo_path, abs_ignore_dirs)

    if crlf_files_found:
        print("🚨 Found files with CRLF line endings:")
        for file_path in sorted(crlf_files_found):
            print(f"  - {file_path}")
        # Exit with a non-zero status code for CI/CD pipeline integration
        exit(1)
    else:
        print("✅ No files with CRLF line endings were found.")
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Checks for CRLF line endings in files within a repository.",
    )

    # fmt: off
    parser.add_argument("root_dir", nargs="?", default=".",
        help="The root directory to scan (default: current directory)")
    parser.add_argument("--ignore", "-i", nargs="+", metavar="DIR", default=[],
        help="One or more directories to ignore.\n(e.g., --ignore build third-party)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    # fmt: on
    args = parser.parse_args()

    repo_path = os.path.abspath(args.root_dir)
    check_crlf_in_root(repo_path, args.ignore, args.verbose)
