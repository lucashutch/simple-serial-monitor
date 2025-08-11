#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import concurrent.futures
import difflib
from simple_utils import colour_str


try:
    max_width = min(os.get_terminal_size()[0], 80)
except OSError:
    max_width = 80

FORMATTER_CONFIG: Dict[str, Dict[str, Any]] = {
    "clang-format": {
        "command": "clang-format",
        "file_extensions": {".h", ".hpp", ".hxx", ".hh", ".c", ".cpp", ".cxx", ".cc"},
        "file_names": set(),
    },
    "cmake-format": {
        "command": "cmake-format",
        "file_extensions": {".cmake"},
        "file_names": {"CMakeLists.txt"},
    },
}


def find_all_files(
    root_dir: Path, ignore_dirs: List[Path], verbose: bool
) -> Dict[Path, Dict[str, Any]]:
    """Finds all files for all configured formatters."""
    files_with_config: Dict[Path, Dict[str, Any]] = {}
    absolute_ignore_dirs = {d.resolve() for d in ignore_dirs}
    if verbose and ignore_dirs:
        print(" Ignored Directories ".center(max_width, "-"))
        for d in absolute_ignore_dirs:
            print(f"  🚫 {d}")
    if not root_dir.is_dir():
        msg = f"Error: Root directory '{root_dir}' not found."
        print(colour_str(msg).red(), file=sys.stderr)
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


def process_one_file(
    file_path: Path, command: str, check: bool
) -> Tuple[str, bool, Optional[str]]:
    """
    Worker function to either check or format a single file.
    In check mode, it returns a diff; otherwise, it formats in-place.
    """
    try:
        original_content = file_path.read_bytes()

        if check:
            cmd = [command, str(file_path)]
            result = subprocess.run(cmd, check=True, capture_output=True)
            new_content = result.stdout
        else:
            cmd = [command, str(file_path), "-i"]
            result = subprocess.run(cmd, check=True, capture_output=True)
            new_content = file_path.read_bytes()

        if original_content == new_content:
            return (str(file_path), False, None)

        if not check:
            return (str(file_path), True, None)

        # Generate a diff for check mode
        original_lines = original_content.decode("utf-8", "ignore").splitlines()
        new_lines = new_content.decode("utf-8", "ignore").splitlines()
        diff = difflib.unified_diff(original_lines, new_lines, lineterm="")
        changed_lines = [
            line
            for line in diff
            if (line.startswith("+") and not line.startswith("+++"))
            or (line.startswith("-") and not line.startswith("---"))
        ]
        return (str(file_path), True, "\n".join(changed_lines))

    except Exception as e:
        error_type = "checking" if check else "formatting"
        print(colour_str(f"Error {error_type} {file_path}: {e}").red(), file=sys.stderr)
        return (str(file_path), False, None)


def process_files_parallel(
    files_with_config: Dict[Path, Dict[str, Any]],
    project_root: Path,
    jobs: Optional[int],
    verbose: bool,
    check: bool,
):
    """Runs the correct formatter or checker in parallel for all found files."""
    if not files_with_config:
        print("No files found to process.")
        return

    if verbose:
        print(" Files Found ".center(max_width, "-"))
        for f in sorted(files_with_config.keys()):
            print(f"  📄 {f.relative_to(project_root)}")

    job_type = "Checking" if check else "Formatting"
    job_str = f"{job_type} using {jobs if jobs else 'all available'} cores"
    print(f"🚀 Found {len(files_with_config)} files. {job_str}.")

    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        future_to_file = {
            executor.submit(process_one_file, path, config["command"], check): path
            for path, config in files_with_config.items()
        }
        for future in concurrent.futures.as_completed(future_to_file):
            try:
                path, was_changed, data = future.result()
                if was_changed:
                    results.append((str(Path(path).relative_to(project_root)), data))
            except Exception as e:
                msg = f"A task generated an exception: {e}"
                print(colour_str(msg).red(), file=sys.stderr)

    if check:
        if not results:
            msg = "✅ Check passed. All files are correctly formatted."
            print(colour_str(msg).green())
            return

        print("\n" + " Files Requiring Formatting ".center(max_width, "-"))
        for f_path, diff_text in sorted(results):
            print(f"\n{colour_str(f'❌ {f_path}').yellow()}")
            for line in diff_text.splitlines():
                if line.startswith("+"):
                    print(colour_str(line).green())
                elif line.startswith("-"):
                    print(colour_str(line).red())
        msg = f"❌ Check failed. {len(results)} files require formatting."
        print(f"\n{colour_str(msg).red().bright()}")
        sys.exit(1)

    else:
        if not results:
            print("✅ All files are already correctly formatted. No changes made.")
            return

        print(" Files Reformatted ".center(max_width, "-"))
        for f_path, _ in sorted(results):
            print(colour_str(f"  ✨ {f_path}").green())
        print(f"✅ Done. {len(results)} files were reformatted.")


def run_project_tasks(
    root_dir: str,
    ignore_dirs: list = [],
    jobs: Optional[int] = None,
    verbose: bool = False,
    check: bool = False,
):
    project_root = Path(root_dir).resolve()
    ignore_paths = [project_root / d for d in ignore_dirs]
    print(f"🚀 Scanning for all source files in: {project_root}")
    files_to_process = find_all_files(project_root, ignore_paths, verbose)
    process_files_parallel(files_to_process, project_root, jobs, verbose, check)


def check_for_tools():
    all_tools_found = True
    for config in FORMATTER_CONFIG.values():
        command = config["command"]
        try:
            subprocess.run([command, "--version"], check=True, capture_output=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(colour_str(f"❌ Error: '{command}' not found.").red())
            all_tools_found = False
    if not all_tools_found:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A universal script to format all source files (C++, CMake, etc.) in parallel.",
    )
    # fmt: off
    parser.add_argument("root_dir", nargs="?", default=".",
        help="The root directory to scan (default: current directory)")

    parser.add_argument("--ignore", "-i", nargs="+", metavar="DIR", default=[],
        help="One or more directories to ignore.\n(e.g., --ignore build third-party)")

    parser.add_argument("-j","--jobs",type=int, default=None,
        help="The number of concurrent jobs to run.\n(default: all available CPU cores)")

    parser.add_argument("-v", "--verbose", action="store_true",
        help="Enable verbose output.")

    parser.add_argument("--check", "-c", action="store_true",
        help="Run in 'check only' mode. Outputs files requiring changes and the associates required changes")
    # fmt: on

    args = parser.parse_args()
    check_for_tools()
    run_project_tasks(args.root_dir, args.ignore, args.jobs, args.verbose, args.check)
