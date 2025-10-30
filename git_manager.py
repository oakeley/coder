"""
Git Manager Module

This module provides git version control functionality for user projects,
enabling change tracking and reversion of unsuccessful edits.
"""

import os
from typing import List, Optional
from git import Repo, InvalidGitRepositoryError
from git.exc import GitCommandError


class GitManager:
    """
    Manages git operations for user projects.

    This class handles repository initialisation, commits, and reversion of changes,
    allowing the system to maintain a complete history of all modifications.
    """

    def __init__(self, project_path: str):
        """
        Initialise the git manager for a specific project.

        Args:
            project_path: The absolute path to the project directory
        """
        # Store the project directory path
        self.project_path = project_path

        # Git repository object (initialised later)
        self.repo: Optional[Repo] = None

        # Check if the directory contains a git repository
        self._initialize_repo()

    def _initialize_repo(self) -> None:
        """
        Initialise or connect to an existing git repository.

        This method checks if a git repository exists at the project path,
        and creates one if it does not exist.
        """
        try:
            # Attempt to open an existing repository
            self.repo = Repo(self.project_path)
        except InvalidGitRepositoryError:
            # No repository exists, create a new one
            self.repo = Repo.init(self.project_path)

            # Create an initial commit
            self._create_initial_commit()

    def _create_initial_commit(self) -> None:
        """
        Create an initial commit for a newly initialised repository.

        This provides a baseline state that can be referred to later.
        """
        try:
            # Create a .gitignore file
            gitignore_path = os.path.join(self.project_path, ".gitignore")

            # Write common Python ignore patterns
            with open(gitignore_path, "w") as f:
                f.write("__pycache__/\n")
                f.write("*.pyc\n")
                f.write("*.pyo\n")
                f.write("*.pyd\n")
                f.write(".Python\n")
                f.write("env/\n")
                f.write("venv/\n")
                f.write(".env\n")
                f.write("*.egg-info/\n")
                f.write("dist/\n")
                f.write("build/\n")

            # Add the gitignore file to the repository
            self.repo.index.add([".gitignore"])

            # Create the initial commit
            self.repo.index.commit("Initial commit - Project created")
        except Exception as e:
            print(f"Warning: Could not create initial commit: {e}")

    def is_repository(self) -> bool:
        """
        Check if the project path contains a valid git repository.

        Returns:
            Boolean indicating whether a valid repository exists
        """
        # Check if the repo object is not None
        return self.repo is not None

    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        Commit changes to the repository.

        Args:
            message: The commit message describing the changes
            files: Optional list of specific files to commit (commits all if None)

        Returns:
            Boolean indicating whether the commit was successful
        """
        try:
            # Check if repository exists
            if not self.repo:
                print("Error: No git repository available")
                return False

            # Add files to the staging area
            if files:
                # Add only the specified files
                self.repo.index.add(files)
            else:
                # Add all modified and untracked files
                self.repo.git.add(A=True)

            # Check if there are any changes to commit
            if not self.repo.index.diff("HEAD") and not self.repo.untracked_files:
                print("No changes to commit")
                return False

            # Create the commit
            self.repo.index.commit(message)

            return True
        except GitCommandError as e:
            print(f"Git error during commit: {e}")
            return False
        except Exception as e:
            print(f"Error committing changes: {e}")
            return False

    def get_commit_history(self, max_count: int = 10) -> List[str]:
        """
        Retrieve the commit history for the repository.

        Args:
            max_count: Maximum number of commits to retrieve

        Returns:
            List of commit descriptions (hash, message, date)
        """
        try:
            # Check if repository exists
            if not self.repo:
                return []

            # Retrieve commits from the repository
            commits = list(self.repo.iter_commits(max_count=max_count))

            # Format commit information
            history = []
            for commit in commits:
                # Format: short hash, date, message
                commit_info = (
                    f"{commit.hexsha[:8]} - "
                    f"{commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} - "
                    f"{commit.message.strip()}"
                )
                history.append(commit_info)

            return history
        except Exception as e:
            print(f"Error retrieving commit history: {e}")
            return []

    def revert_to_commit(self, commit_hash: str) -> bool:
        """
        Revert the repository to a specific commit.

        Args:
            commit_hash: The hash of the commit to revert to

        Returns:
            Boolean indicating whether the reversion was successful
        """
        try:
            # Check if repository exists
            if not self.repo:
                print("Error: No git repository available")
                return False

            # Reset the repository to the specified commit
            self.repo.git.reset("--hard", commit_hash)

            return True
        except GitCommandError as e:
            print(f"Git error during revert: {e}")
            return False
        except Exception as e:
            print(f"Error reverting to commit: {e}")
            return False

    def get_modified_files(self) -> List[str]:
        """
        Get a list of files that have been modified but not committed.

        Returns:
            List of file paths that have been modified
        """
        try:
            # Check if repository exists
            if not self.repo:
                return []

            # Get list of modified files
            modified = [item.a_path for item in self.repo.index.diff(None)]

            # Get list of untracked files
            untracked = self.repo.untracked_files

            # Combine both lists
            return modified + untracked
        except Exception as e:
            print(f"Error getting modified files: {e}")
            return []

    def create_snapshot(self, description: str) -> bool:
        """
        Create a snapshot commit of the current state.

        Args:
            description: A description of the current state

        Returns:
            Boolean indicating whether the snapshot was created
        """
        # Create a commit with a descriptive message
        message = f"Snapshot: {description}"
        return self.commit_changes(message)

    def undo_last_change(self) -> bool:
        """
        Undo the last commit and return to the previous state.

        Returns:
            Boolean indicating whether the undo was successful
        """
        try:
            # Check if repository exists
            if not self.repo:
                print("Error: No git repository available")
                return False

            # Get the parent commit (one before current HEAD)
            if len(list(self.repo.iter_commits())) < 2:
                print("Error: No previous commit to revert to")
                return False

            # Reset to the previous commit
            self.repo.git.reset("--hard", "HEAD~1")

            return True
        except GitCommandError as e:
            print(f"Git error during undo: {e}")
            return False
        except Exception as e:
            print(f"Error undoing last change: {e}")
            return False
