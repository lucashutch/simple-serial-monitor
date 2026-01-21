"""Test code formatter functionality."""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.embedded_cereal_bowl.formatter.formatter import (
    resolve_ignore_dirs,
    scan_directory,
    find_all_files,
    process_one_file,
    FORMATTER_CONFIG,
    check_for_tools,
    run_project_tasks,
    format_files,
    check_format,
)


class TestResolveIgnoreDirs:
    """Test cases for resolve_ignore_dirs function."""

    def test_resolve_ignore_dirs_basic(self):
        """Test basic ignore pattern resolution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create test structure
            (root / "build").mkdir()
            (root / "src").mkdir()
            (root / "vendor").mkdir()

            patterns = ["build", "vendor"]
            result = resolve_ignore_dirs(root, patterns)

            # Should resolve to absolute paths
            expected = {root / "build", root / "vendor"}
            assert result == expected

    def test_resolve_ignore_dirs_with_glob(self):
        """Test ignore patterns with globbing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create nested structure
            (root / "project1" / "build").mkdir(parents=True)
            (root / "project2" / "build").mkdir(parents=True)

            patterns = ["*/build"]
            result = resolve_ignore_dirs(root, patterns)

            expected = {root / "project1" / "build", root / "project2" / "build"}
            assert result == expected

    def test_resolve_ignore_dirs_empty_patterns(self):
        """Test with empty ignore patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = resolve_ignore_dirs(root, [])
            assert result == set()

    def test_resolve_ignore_dirs_nonexistent(self):
        """Test with patterns that don't match anything."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()

            patterns = ["nonexistent", "also_nonexistent"]
            result = resolve_ignore_dirs(root, patterns)
            assert result == set()


class TestScanDirectory:
    """Test cases for scan_directory function."""

    def test_scan_directory_basic(self):
        """Test basic directory scanning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create test structure
            (root / "file1.txt").write_text("content")
            (root / "file2.cpp").write_text("code")
            (root / "subdir").mkdir()
            (root / "subdir" / "file3.h").write_text("header")

            excluded = set()
            result = list(scan_directory(root, excluded))

            # Should return all files recursively
            file_paths = {p.relative_to(root) for p in result}
            expected = {Path("file1.txt"), Path("file2.cpp"), Path("subdir/file3.h")}
            assert file_paths == expected

    def test_scan_directory_with_excluded(self):
        """Test directory scanning with excluded directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create test structure
            (root / "src").mkdir()
            (root / "src" / "main.cpp").write_text("code")
            (root / "build").mkdir()
            (root / "build" / "output.o").write_text("binary")

            excluded = {root / "build"}
            result = list(scan_directory(root, excluded))

            # Should skip excluded directory
            file_paths = {p.relative_to(root) for p in result}
            expected = {Path("src/main.cpp")}
            assert file_paths == expected

    def test_scan_directory_with_symlinks(self):
        """Test that symlinks are ignored."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create file and symlink
            (root / "file.txt").write_text("content")
            (root / "link.txt").symlink_to("file.txt")

            excluded = set()
            result = list(scan_directory(root, excluded))

            # Should only return the real file, not the symlink
            file_paths = {p.name for p in result}
            assert "file.txt" in file_paths
            assert "link.txt" not in file_paths

    def test_scan_directory_permission_error(self):
        """Test handling of permission errors."""
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            mock_iterdir.side_effect = PermissionError("Access denied")

            root = Path("/fake/path")
            excluded = set()
            result = list(scan_directory(root, excluded))

            # Should handle gracefully and return empty list
            assert result == []


class TestFindAllFiles:
    """Test cases for find_all_files function."""

    def test_find_all_files_basic(self):
        """Test finding all files with formatters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create test files
            (root / "test.cpp").write_text("code")
            (root / "test.h").write_text("header")
            (root / "CMakeLists.txt").write_text("cmake")
            (root / "random.txt").write_text("text")

            result = find_all_files(root, [], False)

            # Should find files with known extensions/names
            expected_files = {
                root / "test.cpp",
                root / "test.h",
                root / "CMakeLists.txt",
            }
            assert set(result.keys()) == expected_files

            # Each found file should have associated config
            for file_path in expected_files:
                assert file_path in result
                assert result[file_path] in FORMATTER_CONFIG.values()

    def test_find_all_files_with_ignore_patterns(self):
        """Test finding files with ignore patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create test structure
            (root / "src").mkdir()
            (root / "src" / "main.cpp").write_text("code")
            (root / "build").mkdir()
            (root / "build" / "generated.cpp").write_text("generated")

            ignore_patterns = ["build"]
            result = find_all_files(root, ignore_patterns, False)

            # Should only find files in src, not build
            expected_files = {root / "src/main.cpp"}
            assert set(result.keys()) == expected_files

    def test_find_all_files_no_matches(self):
        """Test when no files match configured formatters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create files that don't match any formatters
            (root / "test.py").write_text("python")
            (root / "test.rb").write_text("ruby")

            result = find_all_files(root, [], False)
            assert result == {}

    def test_find_all_files_nonexistent_directory(self):
        """Test with nonexistent root directory."""
        root = Path("/nonexistent/directory")

        with patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit):
                find_all_files(root, [], False)
                mock_exit.assert_called_once_with(1)
                mock_print.assert_called()


class TestProcessOneFile:
    """Test cases for process_one_file function."""

    def test_process_one_file_no_changes_needed(self):
        """Test processing a file that doesn't need changes."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as f:
            f.write("int x = 1;")
            temp_file = Path(f.name)

        try:
            # Mock subprocess to return same content
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.stdout = b"int x = 1;"
                mock_run.return_value.returncode = 0

                # Create a mock file with read_bytes method
                mock_file = Mock()
                mock_file.read_bytes.return_value = b"int x = 1;"

                with patch("pathlib.Path", return_value=mock_file):
                    result = process_one_file(temp_file, "clang-format", True)

                    path_str, was_changed, diff = result
                    assert path_str == str(temp_file)
                    assert was_changed is False
                    assert diff is None
        finally:
            temp_file.unlink()

    def test_process_one_file_with_changes(self):
        """Test processing a file that needs changes."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as f:
            f.write("int x=1;")  # Badly formatted
            temp_file = Path(f.name)

        try:
            # Mock subprocess to return formatted content
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.stdout = b"int x = 1;"  # Formatted
                mock_run.return_value.returncode = 0

                # Mock file reading to return original content
                with patch("pathlib.Path.read_bytes") as mock_read:
                    original_content = b"int x=1;"
                    formatted_content = b"int x = 1;"
                    mock_read.return_value = original_content

                    result = process_one_file(temp_file, "clang-format", True)

                    path_str, was_changed, diff = result
                    assert path_str == str(temp_file)
                    assert was_changed is True
                    assert diff is not None
                    assert "x=1" in diff or "x = 1" in diff
        finally:
            temp_file.unlink()

    def test_process_one_file_in_place_mode(self):
        """Test processing a file in in-place mode."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as f:
            f.write("int x=1;")
            temp_file = Path(f.name)

        try:
            # Mock subprocess for in-place mode
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                # Mock file reading to simulate file was changed
                with patch("pathlib.Path.read_bytes") as mock_read:
                    original_content = b"int x=1;"
                    changed_content = b"int x = 1;"
                    read_calls = 0

                    def read_side_effect():
                        nonlocal read_calls
                        read_calls += 1
                        return changed_content if read_calls > 1 else original_content

                    mock_read.side_effect = read_side_effect

                    result = process_one_file(temp_file, "clang-format", False)

                    path_str, was_changed, diff = result
                    assert path_str == str(temp_file)
                    assert was_changed is True
                    assert diff is None  # No diff in in-place mode
        finally:
            temp_file.unlink()

    def test_process_one_file_subprocess_error(self):
        """Test handling of subprocess errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as f:
            f.write("int x = 1;")
            temp_file = Path(f.name)

        try:
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, "clang-format")

                result = process_one_file(temp_file, "clang-format", True)

                path_str, was_changed, diff = result
                assert path_str == str(temp_file)
                assert was_changed is False
                assert diff is None
        finally:
            temp_file.unlink()


class TestCheckForTools:
    """Test cases for check_for_tools function."""

    def test_check_for_tools_all_available(self):
        """Test when all required tools are available."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/clang-format"

            # Should not call exit
            with patch("builtins.exit") as mock_exit:
                check_for_tools()
                mock_exit.assert_not_called()

    def test_check_for_tools_missing_tool(self):
        """Test when some tools are missing."""
        with patch("shutil.which") as mock_which:
            with patch("builtins.print") as mock_print:

                def which_side_effect(cmd):
                    return "/usr/bin/cmake-format" if cmd == "cmake-format" else None

                mock_which.side_effect = which_side_effect

                result = check_for_tools()
                assert result is False

                # Should print error for missing tools
                assert mock_print.call_count >= 1


class TestRunProjectTasks:
    """Test cases for run_project_tasks function."""

    def test_run_project_tasks_no_files(self):
        """Test when no files are found to process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            with patch(
                "src.embedded_cereal_bowl.formatter.formatter.find_all_files"
            ) as mock_find:
                mock_find.return_value = {}

                with patch(
                    "src.embedded_cereal_bowl.formatter.formatter.process_files_parallel"
                ) as mock_process:
                    run_project_tasks(root, [], None, False, False)
                    mock_process.assert_called_once_with({}, root, None, False, False)

    def test_run_project_tasks_with_files(self):
        """Test when files are found to process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            mock_config = {"command": "test-formatter"}
            mock_files = {root / "test.cpp": mock_config}

            with patch(
                "src.embedded_cereal_bowl.formatter.formatter.find_all_files"
            ) as mock_find:
                mock_find.return_value = mock_files

                with patch(
                    "src.embedded_cereal_bowl.formatter.formatter.process_files_parallel"
                ) as mock_process:
                    run_project_tasks(root, [], 4, True, True)
                    mock_process.assert_called_once_with(
                        mock_files, root, 4, True, True
                    )


class TestInterfaceFunctions:
    """Test interface functions for programmatic use."""

    def test_format_files(self):
        """Test format_files interface function."""
        with patch(
            "src.embedded_cereal_bowl.formatter.formatter.check_for_tools"
        ) as mock_check:
            with patch(
                "src.embedded_cereal_bowl.formatter.formatter.run_project_tasks"
            ) as mock_run:
                format_files("/test", ["build"], 2, True)
                mock_check.assert_called_once()
                mock_run.assert_called_once_with(
                    root_dir=Path("/test").resolve(),
                    ignore_patterns=["build"],
                    jobs=2,
                    check=False,
                    verbose=True,
                )

    def test_check_format(self):
        """Test check_format interface function."""
        with patch(
            "src.embedded_cereal_bowl.formatter.formatter.check_for_tools"
        ) as mock_check:
            with patch(
                "src.embedded_cereal_bowl.formatter.formatter.run_project_tasks"
            ) as mock_run:
                check_format("/test", ["vendor"], None, False)
                mock_check.assert_called_once()
                mock_run.assert_called_once_with(
                    root_dir=Path("/test").resolve(),
                    ignore_patterns=["vendor"],
                    jobs=None,
                    check=True,
                    verbose=False,
                )
