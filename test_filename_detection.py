#!/usr/bin/env python3
"""
Test script to verify filename detection improvements
"""

from chat_interface import ChatInterface
from ollama_client import OllamaClient
from project_manager import ProjectManager
import tempfile
import shutil


def test_extract_file_mentions():
    """
    Test the file mention extraction method.
    """
    # Create a temporary project
    temp_dir = tempfile.mkdtemp()

    try:
        # Initialize components
        ollama_client = OllamaClient()
        project_manager = ProjectManager()
        project_manager.load_existing_project(temp_dir)

        chat_interface = ChatInterface(ollama_client, project_manager)

        # Test cases
        test_cases = [
            ("Please update the README.md file", ["README.md"]),
            ("Create main.py and helper.py files", ["main.py", "helper.py"]),
            ("Edit src/app.js", ["src/app.js"]),
            ("Update the configuration.json", ["configuration.json"]),
        ]

        print("Testing file mention extraction:")
        for text, expected in test_cases:
            result = chat_interface._extract_file_mentions(text)
            matches = all(exp in result for exp in expected)
            status = "PASS" if matches else "FAIL"
            print(f"  {status}: '{text}' -> {result} (expected: {expected})")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_filename_validation():
    """
    Test the filename validation method.
    """
    # Create a temporary project
    temp_dir = tempfile.mkdtemp()

    try:
        # Initialize components
        ollama_client = OllamaClient()
        project_manager = ProjectManager()
        project_manager.load_existing_project(temp_dir)

        chat_interface = ChatInterface(ollama_client, project_manager)

        # Test cases (filename, should_be_valid)
        test_cases = [
            ("README.md", True),
            ("main.py", True),
            ("src/app.js", True),
            ("ClinicalTrials.gov Search and Report Generator", False),  # Has spaces
            ("# This is a heading", False),  # No extension
            ("file<>.txt", False),  # Invalid characters
            ("a" * 300 + ".txt", False),  # Too long
        ]

        print("\nTesting filename validation:")
        for filename, expected_valid in test_cases:
            result = chat_interface._is_valid_filename(filename)
            status = "PASS" if result == expected_valid else "FAIL"
            print(f"  {status}: '{filename}' -> {result} (expected: {expected_valid})")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("=" * 70)
    print("Filename Detection Test Suite")
    print("=" * 70)

    test_extract_file_mentions()
    test_filename_validation()

    print("\n" + "=" * 70)
    print("Tests complete!")
    print("=" * 70)
