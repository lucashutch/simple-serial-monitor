#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import concurrent.futures

try:
    max_width = min(os.get_terminal_size()[0], 80)
except OSError:
    max_width = 80  # Fallback to a default width if not running in a terminal

# Configuration dictionary for all supported formatters
# fmt: off
FORMATTER_CONFIG: Dict[str, Dict[str, Any]] = {
    "clang-format": {
        "command": "clang-format",
        "file_extensions": {
            ".h", ".hpp", ".hxx", ".hh",
            ".c", ".cpp", ".cxx", ".cc",
        },
        "file_names": set(),
    },
    "cmake-format": {
        "command": "cmake-format",
        "file_extensions": {".cmake"},
        "file_names": {"CMakeLists.txt"},
    },
}  # fmt: on


def find_all_files(
    root_dir: Path, ignore_dirs: List[Path], verbose: bool
) -> Dict[Path, Dict[str, Any]]:
    """
    Finds all files for all configured formatters, returning a dictionary
    mapping each file to its corresponding formatter configuration.
    """
    files_with_config: Dict[Path, Dict[str, Any]] = {}
    absolute_ignore_dirs = {d.resolve() for d in ignore_dirs}
    if verbose and ignore_dirs:
        print(" Ignored Directories ".center(max_width, "-"))
        for d in absolute_ignore_dirs:
            print(f"  🚫 {d}")

    if not root_dir.is_dir():
        print(f"Error: Root directory '{root_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    name_lookup = {
        name: config
        for config in FORMATTER_CONFIG.values()
        for name in config.get("file_names", [])
    }
    extension_lookup = {
        ext: config
        for config in FORMATTER_CONFIG.values()
        for ext in config.get("file_extensions", [])
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # prevents os.walk from ever entering into ignored directories
        dirnames[:] = [
            d
            for d in dirnames
            if (Path(dirpath) / d).resolve() not in absolute_ignore_dirs
        ]

        files_with_config.update(
            {
                Path(dirpath) / filename: config
                for filename in filenames
                if (
                    config := name_lookup.get(filename)
                    or extension_lookup.get(os.path.splitext(filename)[1])
                )
            }
        )

    return files_with_config


def format_one_file(file_path: Path, command: str) -> Tuple[str, bool]:
    """
    Worker function to format a single file using the two-read method.
    """
    try:
        original_content = file_path.read_bytes()
        subprocess.run([command, "-i", str(file_path)], check=True, capture_output=True)
        was_changed = original_content != file_path.read_bytes()
        return (str(file_path), was_changed)
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return (str(file_path), False)


def run_formatter_parallel(
    files_with_config: Dict[Path, Dict[str, Any]],
    project_root: Path,
    jobs: Optional[int],
    verbose: bool,
):
    """
    Runs the correct formatter in parallel for all found files.
    """
    if not files_with_config:
        print("No files found to format.")
        return

    if verbose:
        print(" Files Found ".center(max_width, "-"))
        for f in sorted(files_with_config.keys()):
            print(f"  📄 {f.relative_to(project_root)}")
        job_str = f"{jobs} concurrent jobs" if jobs else "all available CPU cores"
        print(f"🚀 Found {len(files_with_config)} files. Formatting using {job_str}")

    reformatted_files = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        future_to_file = {
            executor.submit(format_one_file, path, config["command"]): path
            for path, config in files_with_config.items()
        }

        for future in concurrent.futures.as_completed(future_to_file):
            try:
                path, was_changed = future.result()
                if was_changed:
                    reformatted_files.append(str(Path(path).relative_to(project_root)))
            except Exception as e:
                print(f"A task generated an exception: {e}", file=sys.stderr)

    if reformatted_files:
        print(" Files Reformatted ".center(max_width, "-"))
        for f_path in sorted(reformatted_files):
            print(f"✨ {f_path}")
        print(f"✅ Done. {len(reformatted_files)} files were reformatted.")
    else:
        print("✅ All files are already correctly formatted. No changes made.")


def format_project(
    root_dir: str,
    ignore_dirs: list = [],
    jobs: Optional[int] = None,
    verbose: bool = False,
):
    project_root = Path(root_dir).resolve()
    ignore_paths = [project_root / d for d in ignore_dirs]

    print(f"🚀 Scanning for all source files in: {project_root}")

    # Finding all files to format
    files_to_format = find_all_files(project_root, ignore_paths, verbose)

    # Format all files found with the appropriate formatter.
    run_formatter_parallel(files_to_format, project_root, jobs, verbose)


def check_for_tools():
    # Check that all configured tools are installed before running
    all_tools_found = True
    for config in FORMATTER_CONFIG.values():
        command = config["command"]
        try:
            subprocess.run([command, "--version"], check=True, capture_output=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"❌ Error: '{command}' not found.")
            all_tools_found = False

    if not all_tools_found:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A universal script to format all source files (C++, CMake, etc.) in parallel.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # fmt: off
    parser.add_argument("root_dir", nargs="?", default=".",
        help="The root directory to scan (default: current directory)")

    parser.add_argument("--ignore", "-i", nargs="+", metavar="DIR", default=[],
        help="One or more directories to ignore.\n(e.g., --ignore build third-party)")

    parser.add_argument("-j","--jobs",type=int, default=None,
        help="The number of concurrent jobs to run.\n(default: all available CPU cores)")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    # fmt: on
    args = parser.parse_args()

    check_for_tools()
    format_project(args.root_dir, args.ignore, args.jobs, args.verbose)
