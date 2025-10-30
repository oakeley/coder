"""
Unit Tests for File Scanner Module

This module contains comprehensive unit tests for the file scanner functionality,
ensuring that project files are correctly discovered and processed.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
from file_scanner import FileScanner


class TestFileScanner(unittest.TestCase):
    """
    Test suite for the FileScanner class.

    Tests directory scanning, file reading, and structure analysis.
    """

    def setUp(self):
        """
        Set up test environment before each test.

        Creates a temporary directory with sample files for testing.
        """
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create sample Python files
        self._create_file("main.py", "print('Hello World')")
        self._create_file("module.py", "def test():\n    pass")

        # Create subdirectory with files
        subdir = Path(self.test_dir) / "subdir"
        subdir.mkdir()
        self._create_file("subdir/helper.py", "# Helper module")

        # Create files that should be excluded
        pycache = Path(self.test_dir) / "__pycache__"
        pycache.mkdir()
        self._create_file("__pycache__/cache.pyc", "binary content")

        # Initialize the file scanner
        self.scanner = FileScanner(self.test_dir)

    def tearDown(self):
        """
        Clean up test environment after each test.

        Removes the temporary directory and all its contents.
        """
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def _create_file(self, relative_path: str, content: str):
        """
        Helper method to create a file with content.

        Args:
            relative_path: Path relative to test directory
            content: Content to write to the file
        """
        # Create the full path
        file_path = Path(self.test_dir) / relative_path

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content
        file_path.write_text(content)

    def test_scan_directory_finds_python_files(self):
        """
        Test that scan_directory finds all Python files.

        Verifies that the scanner discovers all .py files in the directory tree.
        """
        # Scan the directory
        count = self.scanner.scan_directory()

        # Should find 3 Python files (main.py, module.py, subdir/helper.py)
        self.assertEqual(count, 3, "Should find 3 Python files")

    def test_scan_directory_excludes_pycache(self):
        """
        Test that scan_directory excludes __pycache__ directories.

        Verifies that files in excluded directories are not discovered.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Get the list of files
        files = self.scanner.get_file_list()

        # Check that no __pycache__ files are included
        for file_path in files:
            self.assertNotIn("__pycache__", file_path,
                           "__pycache__ files should be excluded")

    def test_get_file_list_returns_sorted_paths(self):
        """
        Test that get_file_list returns sorted relative paths.

        Verifies that file paths are returned in sorted order.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Get the file list
        files = self.scanner.get_file_list()

        # Verify list is sorted
        self.assertEqual(files, sorted(files), "File list should be sorted")

    def test_load_all_files_reads_contents(self):
        """
        Test that load_all_files reads all file contents.

        Verifies that file contents are correctly loaded into memory.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Load all files
        contents = self.scanner.load_all_files()

        # Verify contents are loaded
        self.assertGreater(len(contents), 0, "Should load file contents")

        # Check that main.py content is correct
        self.assertIn("main.py", contents, "Should contain main.py")
        self.assertIn("Hello World", contents["main.py"],
                     "Should contain correct content")

    def test_get_file_content_retrieves_specific_file(self):
        """
        Test that get_file_content retrieves a specific file's content.

        Verifies that individual file contents can be accessed.
        """
        # Scan and load files
        self.scanner.scan_directory()
        self.scanner.load_all_files()

        # Get content of a specific file
        content = self.scanner.get_file_content("module.py")

        # Verify content is correct
        self.assertIn("def test()", content, "Should retrieve correct content")

    def test_get_file_structure_organizes_by_directory(self):
        """
        Test that get_file_structure organizes files by directory.

        Verifies that files are grouped by their parent directories.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Get file structure
        structure = self.scanner.get_file_structure()

        # Verify structure contains directories
        self.assertIn("root", structure, "Should contain root directory")
        self.assertIn("subdir", structure, "Should contain subdir")

        # Verify files are in correct directories
        self.assertIn("main.py", structure["root"],
                     "main.py should be in root")
        self.assertIn("helper.py", structure["subdir"],
                     "helper.py should be in subdir")

    def test_get_statistics_counts_files_and_lines(self):
        """
        Test that get_statistics provides correct counts.

        Verifies that statistics include accurate file and line counts.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Get statistics
        stats = self.scanner.get_statistics()

        # Verify statistics
        self.assertEqual(stats["total_files"], 3, "Should count 3 files")
        self.assertGreater(stats["total_lines"], 0, "Should count lines")
        self.assertGreater(stats["total_chars"], 0, "Should count characters")

    def test_find_files_by_pattern_case_insensitive(self):
        """
        Test that find_files_by_pattern performs case-insensitive search.

        Verifies that file pattern matching is case-insensitive.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Search for files with "main" in the name
        matches = self.scanner.find_files_by_pattern("MAIN")

        # Should find main.py despite case difference
        self.assertEqual(len(matches), 1, "Should find 1 matching file")
        self.assertIn("main.py", matches[0], "Should match main.py")

    def test_find_files_by_pattern_partial_match(self):
        """
        Test that find_files_by_pattern matches partial file names.

        Verifies that pattern matching works for partial strings.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Search for files with "help" in the name
        matches = self.scanner.find_files_by_pattern("help")

        # Should find helper.py
        self.assertEqual(len(matches), 1, "Should find 1 matching file")
        self.assertIn("helper.py", matches[0], "Should match helper.py")

    def test_read_file_handles_missing_file(self):
        """
        Test that read_file handles missing files gracefully.

        Verifies that attempting to read a non-existent file returns empty string.
        """
        # Try to read a non-existent file
        content = self.scanner.read_file(Path(self.test_dir) / "nonexistent.py")

        # Should return empty string
        self.assertEqual(content, "", "Should return empty string for missing file")


class TestFileScannerWithMultipleExtensions(unittest.TestCase):
    """
    Test suite for FileScanner with various file types.

    Tests handling of different source file extensions.
    """

    def setUp(self):
        """
        Set up test environment with multiple file types.
        """
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create files with different extensions
        self._create_file("script.py", "# Python")
        self._create_file("app.js", "// JavaScript")
        self._create_file("style.css", "/* CSS */")
        self._create_file("data.json", "{}")
        self._create_file("readme.md", "# README")

        # Create non-source files
        self._create_file("image.png", "binary")
        self._create_file("document.pdf", "binary")

        # Initialize scanner
        self.scanner = FileScanner(self.test_dir)

    def tearDown(self):
        """
        Clean up test environment.
        """
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def _create_file(self, relative_path: str, content: str):
        """
        Helper method to create a file.
        """
        # Create the full path
        file_path = Path(self.test_dir) / relative_path

        # Write the content
        file_path.write_text(content)

    def test_scan_finds_multiple_extensions(self):
        """
        Test that scanner finds files with different extensions.

        Verifies that various source file types are discovered.
        """
        # Scan the directory
        count = self.scanner.scan_directory()

        # Should find 5 source files (py, js, css, json, md)
        self.assertEqual(count, 5, "Should find 5 source files")

    def test_scan_excludes_binary_files(self):
        """
        Test that scanner excludes binary files.

        Verifies that non-source files like images are not included.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Get file list
        files = self.scanner.get_file_list()

        # Verify binary files are excluded
        self.assertNotIn("image.png", " ".join(files),
                        "Should exclude PNG files")
        self.assertNotIn("document.pdf", " ".join(files),
                        "Should exclude PDF files")

    def test_statistics_by_extension(self):
        """
        Test that statistics include breakdown by extension.

        Verifies that file counts are provided per extension.
        """
        # Scan the directory
        self.scanner.scan_directory()

        # Get statistics
        stats = self.scanner.get_statistics()

        # Verify extension breakdown exists
        self.assertIn("by_extension", stats, "Should include extension breakdown")

        # Check that Python files are counted
        self.assertIn(".py", stats["by_extension"],
                     "Should count Python files")


if __name__ == "__main__":
    # Run the unit tests
    unittest.main()
