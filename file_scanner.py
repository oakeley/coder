"""
File Scanner Module

This module provides functionality to scan and process files in a project directory,
enabling the system to understand the structure and contents of user projects.
"""

import os
from typing import List, Dict, Set
from pathlib import Path


class FileScanner:
    """
    Scans and processes files within a project directory.

    This class identifies relevant source files, reads their contents,
    and organises them for analysis by the AI system.
    """

    # Common source code file extensions to process
    SOURCE_EXTENSIONS = {
        ".py", ".pyw",  # Python
        ".js", ".jsx", ".ts", ".tsx",  # JavaScript/TypeScript
        ".java",  # Java
        ".cpp", ".hpp", ".c", ".h", ".cc", ".cxx",  # C/C++
        ".cs",  # C#
        ".go",  # Go
        ".rs",  # Rust
        ".rb",  # Ruby
        ".php",  # PHP
        ".swift",  # Swift
        ".kt", ".kts",  # Kotlin
        ".scala",  # Scala
        ".r", ".R",  # R
        ".m",  # Objective-C
        ".sql",  # SQL
        ".sh", ".bash",  # Shell scripts
        ".md", ".txt", ".rst",  # Documentation
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",  # Configuration
        ".html", ".css", ".xml"  # Web files
    }

    # Directories to exclude from scanning
    EXCLUDE_DIRS = {
        "__pycache__", ".git", ".svn", ".hg",  # Version control
        "node_modules", "venv", "env", ".env",  # Dependencies
        "build", "dist", ".eggs", "*.egg-info",  # Build artifacts
        ".tox", ".pytest_cache", ".mypy_cache",  # Testing
        "target", "bin", "obj"  # Compiled output
    }

    def __init__(self, project_path: str):
        """
        Initialise the file scanner for a specific project.

        Args:
            project_path: The absolute path to the project directory
        """
        # Store the project directory path
        self.project_path = Path(project_path)

        # Dictionary to store file contents (path -> content)
        self.file_contents: Dict[str, str] = {}

        # List of all discovered source files
        self.source_files: List[Path] = []

    def scan_directory(self) -> int:
        """
        Scan the project directory and identify all relevant source files.

        Returns:
            The number of files discovered
        """
        # Clear any previously scanned data
        self.source_files = []

        # Walk through the project directory
        for root, dirs, files in os.walk(self.project_path):
            # Convert root to Path object
            root_path = Path(root)

            # Remove excluded directories from the search
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            # Process each file in the current directory
            for file in files:
                # Get the full file path
                file_path = root_path / file

                # Check if the file has a relevant extension
                if file_path.suffix in self.SOURCE_EXTENSIONS:
                    self.source_files.append(file_path)

        # Return the count of discovered files
        return len(self.source_files)

    def read_file(self, file_path: Path) -> str:
        """
        Read the contents of a specific file.

        Args:
            file_path: The path to the file to read

        Returns:
            The file contents as a string, or empty string on error
        """
        try:
            # Attempt to read the file with UTF-8 encoding
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return ""
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""

    def load_all_files(self) -> Dict[str, str]:
        """
        Load the contents of all discovered source files.

        Returns:
            Dictionary mapping relative file paths to their contents
        """
        # Clear previous contents
        self.file_contents = {}

        # Read each discovered file
        for file_path in self.source_files:
            # Get the relative path from the project root
            try:
                relative_path = file_path.relative_to(self.project_path)
            except ValueError:
                relative_path = file_path

            # Read the file contents
            content = self.read_file(file_path)

            # Store in the dictionary using relative path as key
            self.file_contents[str(relative_path)] = content

        return self.file_contents

    def get_file_list(self) -> List[str]:
        """
        Get a list of all discovered source file paths.

        Returns:
            List of relative file paths as strings
        """
        # Convert Path objects to relative string paths
        file_list = []
        for file_path in self.source_files:
            try:
                relative_path = file_path.relative_to(self.project_path)
            except ValueError:
                relative_path = file_path
            file_list.append(str(relative_path))

        return sorted(file_list)

    def get_file_structure(self) -> Dict[str, List[str]]:
        """
        Get the directory structure of the project.

        Returns:
            Dictionary mapping directory paths to lists of files they contain
        """
        # Dictionary to store the structure
        structure: Dict[str, List[str]] = {}

        # Process each source file
        for file_path in self.source_files:
            try:
                # Get the relative path
                relative_path = file_path.relative_to(self.project_path)

                # Get the parent directory
                parent_dir = str(relative_path.parent)

                # Use "." for root directory
                if parent_dir == ".":
                    parent_dir = "root"

                # Add the file to the appropriate directory
                if parent_dir not in structure:
                    structure[parent_dir] = []

                structure[parent_dir].append(relative_path.name)
            except ValueError:
                pass

        return structure

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the scanned project.

        Returns:
            Dictionary containing file counts and line counts
        """
        # Statistics dictionary
        stats = {
            "total_files": len(self.source_files),
            "total_lines": 0,
            "total_chars": 0
        }

        # Count by file extension
        extensions: Dict[str, int] = {}

        # Process each file
        for file_path in self.source_files:
            # Count by extension
            ext = file_path.suffix
            extensions[ext] = extensions.get(ext, 0) + 1

            # Count lines and characters
            content = self.read_file(file_path)
            stats["total_lines"] += content.count("\n") + 1
            stats["total_chars"] += len(content)

        # Add extension counts to statistics
        stats["by_extension"] = extensions

        return stats

    def get_file_content(self, relative_path: str) -> str:
        """
        Get the content of a specific file by its relative path.

        Args:
            relative_path: The relative path to the file

        Returns:
            The file content, or empty string if not found
        """
        # Check if the file is in the loaded contents
        if relative_path in self.file_contents:
            return self.file_contents[relative_path]

        # Try to read the file directly
        full_path = self.project_path / relative_path
        if full_path.exists():
            return self.read_file(full_path)

        return ""

    def find_files_by_pattern(self, pattern: str) -> List[str]:
        """
        Find files matching a specific pattern in their name.

        Args:
            pattern: The pattern to search for (case-insensitive)

        Returns:
            List of matching file paths
        """
        # Convert pattern to lowercase for case-insensitive search
        pattern_lower = pattern.lower()

        # Find matching files
        matches = []
        for file_path in self.source_files:
            # Check if pattern is in the file name
            if pattern_lower in file_path.name.lower():
                try:
                    relative_path = file_path.relative_to(self.project_path)
                    matches.append(str(relative_path))
                except ValueError:
                    matches.append(str(file_path))

        return matches
