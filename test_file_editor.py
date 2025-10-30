"""
Unit Tests for File Editor Module

This module contains comprehensive unit tests for the file editor functionality,
ensuring that file modifications are performed safely with proper backup handling.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
from file_editor import FileEditor


class TestFileEditor(unittest.TestCase):
    """
    Test suite for the FileEditor class.

    Tests file reading, writing, backup creation, and safe modification operations.
    """

    def setUp(self):
        """
        Set up test environment before each test.

        Creates a temporary directory for testing file operations.
        """
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Initialize the file editor
        self.editor = FileEditor(self.test_dir)

        # Create a sample file for testing
        self.sample_file = "test.py"
        self.sample_content = "# Sample Python file\nprint('Hello')\n"
        self._create_file(self.sample_file, self.sample_content)

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

    def test_read_file_returns_content(self):
        """
        Test that read_file correctly reads file contents.

        Verifies that file content is read and returned accurately.
        """
        # Read the sample file
        content = self.editor.read_file(self.sample_file)

        # Verify content matches
        self.assertEqual(content, self.sample_content,
                        "Should read correct file content")

    def test_read_nonexistent_file_returns_empty(self):
        """
        Test that reading a non-existent file returns empty string.

        Verifies that the method handles missing files gracefully.
        """
        # Try to read a file that does not exist
        content = self.editor.read_file("nonexistent.py")

        # Should return empty string
        self.assertEqual(content, "", "Should return empty string for missing file")

    def test_write_file_creates_content(self):
        """
        Test that write_file correctly writes new content.

        Verifies that file content is updated with new data.
        """
        # New content to write
        new_content = "# Modified file\nprint('World')\n"

        # Write the new content
        success = self.editor.write_file(self.sample_file, new_content,
                                        create_backup=False)

        # Verify write was successful
        self.assertTrue(success, "Write should succeed")

        # Verify content was updated
        file_path = Path(self.test_dir) / self.sample_file
        actual_content = file_path.read_text()
        self.assertEqual(actual_content, new_content,
                        "File should contain new content")

    def test_write_file_creates_backup(self):
        """
        Test that write_file creates a backup before modifying.

        Verifies that backup files are created when requested.
        """
        # Write new content with backup enabled
        new_content = "# Backup test\n"
        success = self.editor.write_file(self.sample_file, new_content,
                                        create_backup=True)

        # Verify write was successful
        self.assertTrue(success, "Write should succeed")

        # Check that backup directory exists
        backup_dir = Path(self.test_dir) / ".code_assistant_backups"
        self.assertTrue(backup_dir.exists(), "Backup directory should exist")

        # Check that a backup file was created
        backups = list(backup_dir.rglob("*.bak"))
        self.assertGreater(len(backups), 0, "Should create at least one backup")

    def test_create_file_creates_new_file(self):
        """
        Test that create_file creates a new file successfully.

        Verifies that new files can be created with specified content.
        """
        # Create a new file
        new_file = "new_module.py"
        new_content = "# New module\n"
        success = self.editor.create_file(new_file, new_content)

        # Verify creation was successful
        self.assertTrue(success, "File creation should succeed")

        # Verify file exists with correct content
        file_path = Path(self.test_dir) / new_file
        self.assertTrue(file_path.exists(), "File should exist")
        self.assertEqual(file_path.read_text(), new_content,
                        "File should have correct content")

    def test_create_file_fails_if_exists(self):
        """
        Test that create_file fails if the file already exists.

        Verifies that existing files are not overwritten.
        """
        # Try to create a file that already exists
        success = self.editor.create_file(self.sample_file, "# Overwrite attempt")

        # Should fail
        self.assertFalse(success, "Should fail when file exists")

        # Verify original content is unchanged
        content = self.editor.read_file(self.sample_file)
        self.assertEqual(content, self.sample_content,
                        "Original content should be unchanged")

    def test_delete_file_removes_file(self):
        """
        Test that delete_file removes a file successfully.

        Verifies that files can be deleted from the project.
        """
        # Delete the sample file
        success = self.editor.delete_file(self.sample_file, create_backup=False)

        # Verify deletion was successful
        self.assertTrue(success, "Deletion should succeed")

        # Verify file no longer exists
        file_path = Path(self.test_dir) / self.sample_file
        self.assertFalse(file_path.exists(), "File should be deleted")

    def test_delete_file_creates_backup(self):
        """
        Test that delete_file creates a backup before deletion.

        Verifies that deleted files can be recovered from backups.
        """
        # Delete the file with backup enabled
        success = self.editor.delete_file(self.sample_file, create_backup=True)

        # Verify deletion was successful
        self.assertTrue(success, "Deletion should succeed")

        # Check that a backup was created
        backup_dir = Path(self.test_dir) / ".code_assistant_backups"
        backups = list(backup_dir.rglob("*.bak"))
        self.assertGreater(len(backups), 0, "Should create a backup")

    def test_append_to_file_adds_content(self):
        """
        Test that append_to_file adds content to the end of a file.

        Verifies that content can be appended without overwriting.
        """
        # Append content to the file
        append_content = "# Appended line\n"
        success = self.editor.append_to_file(self.sample_file, append_content,
                                            create_backup=False)

        # Verify append was successful
        self.assertTrue(success, "Append should succeed")

        # Verify content includes both original and appended
        content = self.editor.read_file(self.sample_file)
        self.assertIn(self.sample_content, content,
                     "Should contain original content")
        self.assertIn(append_content, content, "Should contain appended content")

    def test_replace_in_file_substitutes_text(self):
        """
        Test that replace_in_file correctly replaces text.

        Verifies that text substitution works as expected.
        """
        # Replace text in the file
        success = self.editor.replace_in_file(self.sample_file, "Hello", "Goodbye",
                                             create_backup=False)

        # Verify replacement was successful
        self.assertTrue(success, "Replace should succeed")

        # Verify text was replaced
        content = self.editor.read_file(self.sample_file)
        self.assertIn("Goodbye", content, "Should contain new text")
        self.assertNotIn("Hello", content, "Should not contain old text")

    def test_replace_in_file_fails_if_text_not_found(self):
        """
        Test that replace_in_file fails if the text is not found.

        Verifies that the method handles missing text correctly.
        """
        # Try to replace text that does not exist
        success = self.editor.replace_in_file(self.sample_file,
                                             "NonexistentText", "NewText",
                                             create_backup=False)

        # Should fail
        self.assertFalse(success, "Should fail when text not found")

    def test_get_backup_list_returns_backups(self):
        """
        Test that get_backup_list returns all backup files.

        Verifies that backup files can be enumerated.
        """
        # Create some backups by modifying files
        self.editor.write_file(self.sample_file, "# Version 1", create_backup=True)
        self.editor.write_file(self.sample_file, "# Version 2", create_backup=True)

        # Get backup list
        backups = self.editor.get_backup_list()

        # Should have at least 2 backups
        self.assertGreaterEqual(len(backups), 2, "Should have at least 2 backups")

    def test_restore_from_backup_recovers_content(self):
        """
        Test that restore_from_backup recovers file content.

        Verifies that files can be restored from backup copies.
        """
        # Save original content
        original_content = self.editor.read_file(self.sample_file)

        # Modify the file with backup
        self.editor.write_file(self.sample_file, "# Modified", create_backup=True)

        # Get the backup file
        backups = self.editor.get_backup_list()
        self.assertGreater(len(backups), 0, "Should have a backup")

        # Restore from backup
        success = self.editor.restore_from_backup(backups[0], self.sample_file)

        # Verify restoration was successful
        self.assertTrue(success, "Restore should succeed")

        # Verify content is restored
        restored_content = self.editor.read_file(self.sample_file)
        self.assertEqual(restored_content, original_content,
                        "Content should be restored")


class TestFileEditorWithSubdirectories(unittest.TestCase):
    """
    Test suite for FileEditor with nested directories.

    Tests handling of files in subdirectories.
    """

    def setUp(self):
        """
        Set up test environment with subdirectories.
        """
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Initialize editor
        self.editor = FileEditor(self.test_dir)

    def tearDown(self):
        """
        Clean up test environment.
        """
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_create_file_in_subdirectory(self):
        """
        Test creating a file in a subdirectory.

        Verifies that parent directories are created automatically.
        """
        # Create a file in a nested subdirectory
        nested_file = "subdir/module/test.py"
        content = "# Nested file"
        success = self.editor.create_file(nested_file, content)

        # Verify creation was successful
        self.assertTrue(success, "Should create file in subdirectory")

        # Verify file exists
        file_path = Path(self.test_dir) / nested_file
        self.assertTrue(file_path.exists(), "File should exist")

    def test_write_file_in_subdirectory(self):
        """
        Test writing to a file in a subdirectory.

        Verifies that subdirectory files can be modified.
        """
        # Create a file in a subdirectory
        subdir_file = "modules/helper.py"
        self.editor.create_file(subdir_file, "# Original")

        # Modify the file
        new_content = "# Modified"
        success = self.editor.write_file(subdir_file, new_content,
                                        create_backup=False)

        # Verify write was successful
        self.assertTrue(success, "Should write to subdirectory file")

        # Verify content is updated
        content = self.editor.read_file(subdir_file)
        self.assertEqual(content, new_content, "Content should be updated")


if __name__ == "__main__":
    # Run the unit tests
    unittest.main()
