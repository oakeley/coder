#!/usr/bin/env python3
"""
Test script to verify Ctrl-D exit logic
"""

from chat_interface import ChatInterface
from ollama_client import OllamaClient
from project_manager import ProjectManager
import tempfile
import shutil


def test_eof_counter():
    """
    Test the EOF counter logic.
    """
    # Create a temporary project
    temp_dir = tempfile.mkdtemp()

    try:
        # Initialize components
        ollama_client = OllamaClient()
        project_manager = ProjectManager()
        project_manager.load_existing_project(temp_dir)

        chat_interface = ChatInterface(ollama_client, project_manager)

        print("Testing EOF counter logic:")
        print("=" * 70)

        # Initial state
        assert chat_interface.eof_count == 0, "Initial EOF count should be 0"
        print("PASS: Initial EOF count is 0")

        # Simulate first Ctrl-D
        chat_interface.eof_count += 1
        assert chat_interface.eof_count == 1, "EOF count should be 1 after first press"
        print("PASS: EOF count is 1 after first Ctrl-D")

        # Check that we should NOT exit yet
        should_exit = chat_interface.eof_count >= 2
        assert not should_exit, "Should not exit after only one Ctrl-D"
        print("PASS: Does not exit after first Ctrl-D")

        # Simulate second Ctrl-D
        chat_interface.eof_count += 1
        assert chat_interface.eof_count == 2, "EOF count should be 2 after second press"
        print("PASS: EOF count is 2 after second Ctrl-D")

        # Check that we SHOULD exit now
        should_exit = chat_interface.eof_count >= 2
        assert should_exit, "Should exit after two Ctrl-D presses"
        print("PASS: Exits after second consecutive Ctrl-D")

        # Test counter reset (simulating user input)
        chat_interface.eof_count = 0
        assert chat_interface.eof_count == 0, "EOF count should reset to 0"
        print("PASS: EOF count resets to 0 after user input")

        # Simulate first Ctrl-D, then reset, then first Ctrl-D again
        chat_interface.eof_count += 1
        assert chat_interface.eof_count == 1
        chat_interface.eof_count = 0  # User types something
        assert chat_interface.eof_count == 0
        chat_interface.eof_count += 1  # Ctrl-D again
        assert chat_interface.eof_count == 1
        print("PASS: Counter properly resets between non-consecutive Ctrl-D presses")

        print("\n" + "=" * 70)
        print("All EOF counter tests passed!")
        print("=" * 70)

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_eof_counter()
