"""
File Editor Module

This module provides safe file editing capabilities with backup and validation,
enabling the system to modify source files while maintaining integrity.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime


class FileEditor:
    """
    Handles safe editing of project files.

    This class provides methods to modify files while creating backups,
    allowing for easy reversion if changes are unsuccessful.
    """

    def __init__(self, project_path: str):
        """
        Initialise the file editor for a specific project.

        Args:
            project_path: The absolute path to the project directory
        """
        # Store the project directory path
        self.project_path = Path(project_path)

        # Directory for storing backup files
        self.backup_dir = self.project_path / ".code_assistant_backups"

        # Ensure backup directory exists
        self._ensure_backup_dir()

    def _ensure_backup_dir(self) -> None:
        """
        Ensure that the backup directory exists.

        Creates the directory if it does not already exist.
        """
        try:
            # Create the backup directory if needed
            self.backup_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create backup directory: {e}")

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of a file before modification.

        Args:
            file_path: The path to the file to backup

        Returns:
            Path to the backup file, or None if backup failed
        """
        try:
            # Get the relative path from project root
            relative_path = file_path.relative_to(self.project_path)

            # Create a timestamp for the backup (includes microseconds for uniqueness)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            # Generate backup file name
            backup_name = f"{relative_path.name}.{timestamp}.bak"

            # Create subdirectory structure in backup directory
            backup_subdir = self.backup_dir / relative_path.parent
            backup_subdir.mkdir(parents=True, exist_ok=True)

            # Full path to the backup file
            backup_path = backup_subdir / backup_name

            # Copy the file to the backup location
            shutil.copy2(file_path, backup_path)

            return backup_path
        except Exception as e:
            print(f"Error creating backup for {file_path}: {e}")
            return None

    def read_file(self, relative_path: str) -> str:
        """
        Read the contents of a file.

        Args:
            relative_path: The relative path to the file from project root

        Returns:
            The file contents as a string
        """
        # Construct the full file path
        file_path = self.project_path / relative_path

        try:
            # Read the file with UTF-8 encoding
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file {relative_path}: {e}")
                return ""
        except Exception as e:
            print(f"Error reading file {relative_path}: {e}")
            return ""

    def write_file(self, relative_path: str, content: str, create_backup: bool = True) -> bool:
        """
        Write content to a file, optionally creating a backup first.

        Args:
            relative_path: The relative path to the file from project root
            content: The new content to write to the file
            create_backup: Whether to create a backup before writing

        Returns:
            Boolean indicating whether the write was successful
        """
        # Construct the full file path
        file_path = self.project_path / relative_path

        # Create backup if file exists and backup is requested
        if create_backup and file_path.exists():
            backup_path = self._create_backup(file_path)
            if backup_path:
                print(f"Backup created: {backup_path}")

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the content to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error writing file {relative_path}: {e}")
            return False

    def create_file(self, relative_path: str, content: str) -> bool:
        """
        Create a new file with the specified content.

        Args:
            relative_path: The relative path to the new file from project root
            content: The content to write to the new file

        Returns:
            Boolean indicating whether the file was created successfully
        """
        # Construct the full file path
        file_path = self.project_path / relative_path

        # Check if file already exists
        if file_path.exists():
            print(f"Error: File {relative_path} already exists")
            return False

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the content to the new file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error creating file {relative_path}: {e}")
            return False

    def delete_file(self, relative_path: str, create_backup: bool = True) -> bool:
        """
        Delete a file, optionally creating a backup first.

        Args:
            relative_path: The relative path to the file from project root
            create_backup: Whether to create a backup before deleting

        Returns:
            Boolean indicating whether the deletion was successful
        """
        # Construct the full file path
        file_path = self.project_path / relative_path

        # Check if file exists
        if not file_path.exists():
            print(f"Error: File {relative_path} does not exist")
            return False

        # Create backup if requested
        if create_backup:
            backup_path = self._create_backup(file_path)
            if backup_path:
                print(f"Backup created: {backup_path}")

        try:
            # Delete the file
            file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file {relative_path}: {e}")
            return False

    def append_to_file(self, relative_path: str, content: str, create_backup: bool = True) -> bool:
        """
        Append content to an existing file.

        Args:
            relative_path: The relative path to the file from project root
            content: The content to append to the file
            create_backup: Whether to create a backup before appending

        Returns:
            Boolean indicating whether the append was successful
        """
        # Construct the full file path
        file_path = self.project_path / relative_path

        # Check if file exists
        if not file_path.exists():
            print(f"Error: File {relative_path} does not exist")
            return False

        # Create backup if requested
        if create_backup:
            backup_path = self._create_backup(file_path)
            if backup_path:
                print(f"Backup created: {backup_path}")

        try:
            # Append content to the file
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error appending to file {relative_path}: {e}")
            return False

    def replace_in_file(self, relative_path: str, old_text: str, new_text: str,
                       create_backup: bool = True) -> bool:
        """
        Replace text within a file.

        Args:
            relative_path: The relative path to the file from project root
            old_text: The text to search for
            new_text: The text to replace it with
            create_backup: Whether to create a backup before replacing

        Returns:
            Boolean indicating whether the replacement was successful
        """
        # Read the current file content
        content = self.read_file(relative_path)

        # Check if the old text exists in the file
        if old_text not in content:
            print(f"Error: Text not found in file {relative_path}")
            return False

        # Perform the replacement
        new_content = content.replace(old_text, new_text)

        # Write the modified content back to the file
        return self.write_file(relative_path, new_content, create_backup)

    def get_backup_list(self) -> list:
        """
        Get a list of all backup files.

        Returns:
            List of backup file paths
        """
        try:
            # Find all backup files
            backups = []
            for root, dirs, files in os.walk(self.backup_dir):
                for file in files:
                    if file.endswith(".bak"):
                        backups.append(os.path.join(root, file))
            return backups
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []

    def restore_from_backup(self, backup_path: str, relative_path: str) -> bool:
        """
        Restore a file from a backup.

        Args:
            backup_path: The path to the backup file
            relative_path: The relative path where the file should be restored

        Returns:
            Boolean indicating whether the restoration was successful
        """
        try:
            # Construct the full file path
            file_path = self.project_path / relative_path

            # Copy the backup to the original location
            shutil.copy2(backup_path, file_path)

            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False
