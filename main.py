#!/usr/bin/env python3
"""
Code Assistant Main Application

This is the main entry point for the Code Assistant tool, which provides
an AI-powered interface for managing and editing code projects using
a local Ollama qwen3-coder:30b model.
"""

import sys
import os
from pathlib import Path
from ollama_client import OllamaClient
from project_manager import ProjectManager
from chat_interface import ChatInterface


def print_banner():
    """
    Print the application banner.
    """
    print("\n" + "=" * 70)
    print("Code Assistant - AI-Powered Code Management Tool")
    print("=" * 70)
    print("Using Ollama qwen3-coder:30b with 128K token context")
    print("=" * 70 + "\n")


def test_ollama_connection(client: OllamaClient) -> bool:
    """
    Test the connection to the Ollama API server.

    Args:
        client: The Ollama client to test

    Returns:
        Boolean indicating whether the connection is successful
    """
    print("Testing connection to Ollama API...")

    if client.test_connection():
        print("Successfully connected to Ollama API\n")
        return True
    else:
        print("ERROR: Could not connect to Ollama API")
        print("Please ensure that:")
        print("  1. Ollama is installed and running")
        print("  2. The qwen3-coder:30b model is available")
        print("  3. The Ollama server is accessible at http://localhost:11434")
        print("\nTo install the model, run:")
        print("  ollama pull qwen3-coder:30b\n")
        return False


def get_user_input(prompt_text: str) -> str:
    """
    Get input from the user with a prompt.

    Args:
        prompt_text: The prompt to display

    Returns:
        The user's input as a string
    """
    try:
        return input(prompt_text).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled")
        sys.exit(0)


def setup_project(project_manager: ProjectManager) -> bool:
    """
    Set up a project (new or existing).

    Args:
        project_manager: The project manager instance

    Returns:
        Boolean indicating whether project setup was successful
    """
    print("Project Setup")
    print("-" * 70)

    # Ask if user wants to create a new project
    choice = get_user_input("Would you like to create a new project? (yes/no): ").lower()

    if choice in ["yes", "y"]:
        # Create a new project
        return create_new_project(project_manager)
    elif choice in ["no", "n"]:
        # Use existing project
        return load_existing_project(project_manager)
    else:
        print("Invalid choice. Please enter 'yes' or 'no'")
        return setup_project(project_manager)


def create_new_project(project_manager: ProjectManager) -> bool:
    """
    Create a new project with user input.

    Args:
        project_manager: The project manager instance

    Returns:
        Boolean indicating whether the project was created successfully
    """
    print("\nCreating New Project")
    print("-" * 70)

    # Get project path
    default_path = os.path.join(os.getcwd(), "my_project")
    project_path = get_user_input(f"Enter project path (default: {default_path}): ")

    if not project_path:
        project_path = default_path

    # Get project description
    print("\nPlease describe the project:")
    print("(This will help the AI understand what you want to build)")
    description = get_user_input("Description: ")

    if not description:
        description = "A new software project"

    # Create the project
    print(f"\nCreating project at: {project_path}")
    success = project_manager.create_new_project(project_path, description)

    if success:
        print("Project created successfully!")
        print(f"Project initialized with git repository")
        return True
    else:
        print("Failed to create project")
        return False


def load_existing_project(project_manager: ProjectManager) -> bool:
    """
    Load an existing project.

    Args:
        project_manager: The project manager instance

    Returns:
        Boolean indicating whether the project was loaded successfully
    """
    print("\nLoading Existing Project")
    print("-" * 70)

    # Get project path
    default_path = os.getcwd()
    project_path = get_user_input(f"Enter project path (default: current directory): ")

    if not project_path:
        project_path = default_path

    # Load the project
    print(f"\nLoading project from: {project_path}")
    success = project_manager.load_existing_project(project_path)

    if success:
        print("Project loaded successfully!")

        # Display project information
        info = project_manager.get_project_info()
        if "statistics" in info:
            stats = info["statistics"]
            print(f"Found {stats.get('total_files', 0)} source files")
            print(f"Total lines of code: {stats.get('total_lines', 0)}")

        # Check if git repository exists
        if info.get("has_git", False):
            print("Git repository detected")
        else:
            print("No git repository found - one will be created")

        return True
    else:
        print("Failed to load project")
        return False


def main():
    """
    Main application entry point.

    This function orchestrates the setup and execution of the Code Assistant tool.
    """
    # Print the application banner
    print_banner()

    # Initialize the Ollama client
    ollama_client = OllamaClient(model_name="qwen3-coder:30b")

    # Test the connection to Ollama
    if not test_ollama_connection(ollama_client):
        sys.exit(1)

    # Initialize the project manager
    project_manager = ProjectManager()

    # Set up the project (new or existing)
    if not setup_project(project_manager):
        print("\nFailed to set up project. Exiting.")
        sys.exit(1)

    # Initialize the chat interface
    print("\nInitializing chat interface...")
    chat_interface = ChatInterface(ollama_client, project_manager)

    # Display usage information
    print("\nThe AI assistant is now ready to help with your project.")
    print("You can:")
    print("  - Ask questions about your code")
    print("  - Request improvements or bug fixes")
    print("  - Get explanations of how things work")
    print("\nAll changes will be proposed before implementation.")
    print("Use /approve to accept changes, /reject to decline them.")
    print("Type /help for more commands.\n")

    # Run the chat interface
    try:
        chat_interface.run()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
