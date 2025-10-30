"""
Unit Tests for Git Manager Module

This module contains comprehensive unit tests for the git manager functionality,
ensuring that version control operations work correctly and reliably.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
from git_manager import GitManager


class TestGitManager(unittest.TestCase):
    """
    Test suite for the GitManager class.

    Tests initialization, commits, history retrieval, and reversion operations.
    """

    def setUp(self):
        """
        Set up test environment before each test.

        Creates a temporary directory for testing git operations.
        """
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Initialize the git manager
        self.git_manager = GitManager(self.test_dir)

    def tearDown(self):
        """
        Clean up test environment after each test.

        Removes the temporary directory and all its contents.
        """
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_initialization_creates_repository(self):
        """
        Test that initialization creates a git repository.

        Verifies that a .git directory is created in the project path.
        """
        # Check if .git directory exists
        git_dir = Path(self.test_dir) / ".git"
        self.assertTrue(git_dir.exists(), "Git directory should be created")
        self.assertTrue(git_dir.is_dir(), "Git directory should be a directory")

    def test_is_repository_returns_true(self):
        """
        Test that is_repository correctly identifies a valid repository.

        Verifies that the method returns True for an initialized repository.
        """
        # Check if repository is valid
        self.assertTrue(self.git_manager.is_repository(),
                       "Should recognize valid repository")

    def test_commit_changes_with_new_file(self):
        """
        Test committing a new file to the repository.

        Creates a test file and verifies it can be committed successfully.
        """
        # Create a test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Test content")

        # Commit the file
        success = self.git_manager.commit_changes("Add test file", ["test.txt"])

        # Verify commit was successful
        self.assertTrue(success, "Commit should succeed")

    def test_commit_changes_without_files(self):
        """
        Test that committing with no changes returns False.

        Verifies that the method handles the no-changes case correctly.
        """
        # Try to commit without any changes
        success = self.git_manager.commit_changes("Empty commit")

        # Should return False when there are no changes
        self.assertFalse(success, "Should fail when no changes exist")

    def test_get_commit_history(self):
        """
        Test retrieving commit history.

        Creates multiple commits and verifies they appear in the history.
        """
        # Create and commit a test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Initial content")
        self.git_manager.commit_changes("First commit", ["test.txt"])

        # Modify and commit again
        test_file.write_text("Modified content")
        self.git_manager.commit_changes("Second commit", ["test.txt"])

        # Get commit history
        history = self.git_manager.get_commit_history()

        # Verify history contains commits
        self.assertGreater(len(history), 0, "History should contain commits")

        # Check that recent commits are in the history
        history_text = " ".join(history)
        self.assertIn("Second commit", history_text, "Should contain second commit")

    def test_create_snapshot(self):
        """
        Test creating a snapshot of the current state.

        Verifies that snapshots can be created with descriptive messages.
        """
        # Create a test file
        test_file = Path(self.test_dir) / "snapshot_test.txt"
        test_file.write_text("Snapshot content")

        # Create a snapshot
        success = self.git_manager.create_snapshot("Test snapshot")

        # Verify snapshot was created
        self.assertTrue(success, "Snapshot should be created successfully")

        # Check commit history contains the snapshot
        history = self.git_manager.get_commit_history()
        history_text = " ".join(history)
        self.assertIn("Snapshot: Test snapshot", history_text,
                     "History should contain snapshot commit")

    def test_get_modified_files(self):
        """
        Test retrieving a list of modified files.

        Creates an uncommitted file and verifies it appears in the modified list.
        """
        # Create a test file without committing
        test_file = Path(self.test_dir) / "modified.txt"
        test_file.write_text("Modified content")

        # Get list of modified files
        modified = self.git_manager.get_modified_files()

        # Verify the file appears in the list
        self.assertIn("modified.txt", modified,
                     "Modified file should appear in the list")

    def test_undo_last_change(self):
        """
        Test undoing the last commit.

        Creates two commits and verifies that undoing reverts to the first.
        """
        # Create and commit first file
        test_file = Path(self.test_dir) / "undo_test.txt"
        test_file.write_text("First version")
        self.git_manager.commit_changes("First version", ["undo_test.txt"])

        # Modify and commit again
        test_file.write_text("Second version")
        self.git_manager.commit_changes("Second version", ["undo_test.txt"])

        # Undo the last change
        success = self.git_manager.undo_last_change()

        # Verify undo was successful
        self.assertTrue(success, "Undo should succeed")

        # Verify file content is reverted
        content = test_file.read_text()
        self.assertEqual(content, "First version",
                        "Content should be reverted to first version")

    def test_revert_to_specific_commit(self):
        """
        Test reverting to a specific commit by hash.

        Creates multiple commits and reverts to an earlier one.
        """
        # Create and commit first file
        test_file = Path(self.test_dir) / "revert_test.txt"
        test_file.write_text("Version 1")
        self.git_manager.commit_changes("Version 1", ["revert_test.txt"])

        # Get the commit hash
        history = self.git_manager.get_commit_history()
        first_commit_hash = history[0].split()[0]  # Extract hash from first commit

        # Create another commit
        test_file.write_text("Version 2")
        self.git_manager.commit_changes("Version 2", ["revert_test.txt"])

        # Revert to the first commit
        success = self.git_manager.revert_to_commit(first_commit_hash)

        # Verify revert was successful
        self.assertTrue(success, "Revert should succeed")

        # Verify file content is reverted
        content = test_file.read_text()
        self.assertEqual(content, "Version 1",
                        "Content should be reverted to version 1")


class TestGitManagerEdgeCases(unittest.TestCase):
    """
    Test suite for edge cases in GitManager.

    Tests error handling and boundary conditions.
    """

    def setUp(self):
        """
        Set up test environment before each test.
        """
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        Clean up test environment after each test.
        """
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_invalid_commit_hash(self):
        """
        Test reverting to an invalid commit hash.

        Verifies that the method handles invalid hashes gracefully.
        """
        # Initialize git manager
        git_manager = GitManager(self.test_dir)

        # Try to revert to an invalid hash
        success = git_manager.revert_to_commit("invalid_hash_12345")

        # Should return False for invalid hash
        self.assertFalse(success, "Should fail with invalid commit hash")

    def test_undo_with_no_previous_commit(self):
        """
        Test undoing when there is no previous commit to revert to.

        Verifies that the method handles this edge case correctly.
        """
        # Initialize git manager (will have initial commit)
        git_manager = GitManager(self.test_dir)

        # Try to undo (only initial commit exists)
        success = git_manager.undo_last_change()

        # Should return False when there's no previous commit
        self.assertFalse(success, "Should fail when no previous commit exists")


if __name__ == "__main__":
    # Run the unit tests
    unittest.main()
