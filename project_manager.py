"""
Project Manager Module

This module handles project initialisation and management,
including creating new projects and loading existing ones.
"""

import os
from pathlib import Path
from typing import Optional, Dict
from git_manager import GitManager
from file_scanner import FileScanner
from file_editor import FileEditor


class ProjectManager:
    """
    Manages project lifecycle and configuration.

    This class handles the creation of new projects and loading of existing projects,
    coordinating the various subsystems required for project management.
    """

    def __init__(self):
        """
        Initialise the project manager.
        """
        # Path to the current project
        self.project_path: Optional[Path] = None

        # Git manager instance for version control
        self.git_manager: Optional[GitManager] = None

        # File scanner for reading project files
        self.file_scanner: Optional[FileScanner] = None

        # File editor for modifying files
        self.file_editor: Optional[FileEditor] = None

        # Project metadata
        self.project_description: str = ""

    def create_new_project(self, project_path: str, description: str) -> bool:
        """
        Create a new project with the specified description.

        Args:
            project_path: The path where the project should be created
            description: A description of what the project should do

        Returns:
            Boolean indicating whether the project was created successfully
        """
        try:
            # Convert to Path object
            self.project_path = Path(project_path).resolve()

            # Store the project description
            self.project_description = description

            # Create the project directory if it does not exist
            self.project_path.mkdir(parents=True, exist_ok=True)

            # Initialise git manager (creates repository)
            self.git_manager = GitManager(str(self.project_path))

            # Initialise file scanner
            self.file_scanner = FileScanner(str(self.project_path))

            # Initialise file editor
            self.file_editor = FileEditor(str(self.project_path))

            # Create a README file with the project description
            readme_path = "README.md"
            readme_content = f"""# Project

## Description
{description}

## Notes
This project was created and is managed by the Code Assistant tool.
"""
            self.file_editor.create_file(readme_path, readme_content)

            # Commit the initial project structure
            self.git_manager.commit_changes("Initial project setup with README")

            return True
        except Exception as e:
            print(f"Error creating new project: {e}")
            return False

    def load_existing_project(self, project_path: str) -> bool:
        """
        Load an existing project from the specified path.

        Args:
            project_path: The path to the existing project

        Returns:
            Boolean indicating whether the project was loaded successfully
        """
        try:
            # Convert to Path object
            self.project_path = Path(project_path).resolve()

            # Check if the directory exists
            if not self.project_path.exists():
                print(f"Error: Directory {project_path} does not exist")
                return False

            # Check if the directory is accessible
            if not self.project_path.is_dir():
                print(f"Error: {project_path} is not a directory")
                return False

            # Initialise git manager (creates repository if needed)
            self.git_manager = GitManager(str(self.project_path))

            # Initialise file scanner
            self.file_scanner = FileScanner(str(self.project_path))

            # Initialise file editor
            self.file_editor = FileEditor(str(self.project_path))

            # Try to load project description from README
            readme_path = self.project_path / "README.md"
            if readme_path.exists():
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        # Read the first few lines as description
                        lines = f.readlines()
                        if len(lines) > 2:
                            self.project_description = "".join(lines[2:10]).strip()
                except Exception:
                    pass

            # Scan the project files
            file_count = self.file_scanner.scan_directory()
            print(f"Loaded project with {file_count} source files")

            return True
        except Exception as e:
            print(f"Error loading existing project: {e}")
            return False

    def get_project_info(self) -> Dict[str, any]:
        """
        Get information about the current project.

        Returns:
            Dictionary containing project information
        """
        if not self.project_path:
            return {"status": "No project loaded"}

        # Gather project information
        info = {
            "path": str(self.project_path),
            "description": self.project_description,
            "has_git": self.git_manager.is_repository() if self.git_manager else False
        }

        # Add file statistics if available
        if self.file_scanner:
            info["statistics"] = self.file_scanner.get_statistics()

        # Add git information if available
        if self.git_manager:
            info["recent_commits"] = self.git_manager.get_commit_history(5)
            info["modified_files"] = self.git_manager.get_modified_files()

        return info

    def create_snapshot(self, description: str) -> bool:
        """
        Create a snapshot of the current project state.

        Args:
            description: A description of the current state

        Returns:
            Boolean indicating whether the snapshot was created
        """
        if not self.git_manager:
            print("Error: No git manager available")
            return False

        return self.git_manager.create_snapshot(description)

    def revert_changes(self, commit_hash: Optional[str] = None) -> bool:
        """
        Revert changes to a previous state.

        Args:
            commit_hash: Optional specific commit to revert to (reverts last if None)

        Returns:
            Boolean indicating whether the reversion was successful
        """
        if not self.git_manager:
            print("Error: No git manager available")
            return False

        if commit_hash:
            return self.git_manager.revert_to_commit(commit_hash)
        else:
            return self.git_manager.undo_last_change()

    def get_file_list(self) -> list:
        """
        Get a list of all files in the project.

        Returns:
            List of file paths
        """
        if not self.file_scanner:
            return []

        return self.file_scanner.get_file_list()

    def get_file_content(self, relative_path: str) -> str:
        """
        Get the content of a specific file.

        Args:
            relative_path: The relative path to the file

        Returns:
            The file content
        """
        if not self.file_editor:
            return ""

        return self.file_editor.read_file(relative_path)

    def is_project_loaded(self) -> bool:
        """
        Check if a project is currently loaded.

        Returns:
            Boolean indicating whether a project is loaded
        """
        return self.project_path is not None
