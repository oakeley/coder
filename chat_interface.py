"""
Chat Interface Module

This module provides an interactive chat interface for communicating with the AI,
including a proposal system for reviewing changes before implementation.
"""

from typing import List, Dict, Optional
import re
import sys
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from ollama_client import OllamaClient
from project_manager import ProjectManager


class ChatInterface:
    """
    Interactive chat interface for discussing code with the AI.

    This class manages conversations, proposals for changes, and user feedback,
    ensuring all modifications are reviewed before implementation.
    """

    def __init__(self, ollama_client: OllamaClient, project_manager: ProjectManager):
        """
        Initialise the chat interface.

        Args:
            ollama_client: The Ollama client for AI interactions
            project_manager: The project manager for file operations
        """
        # Store the Ollama client reference
        self.ollama_client = ollama_client

        # Store the project manager reference
        self.project_manager = project_manager

        # Chat history (list of message dictionaries)
        self.chat_history: List[Dict[str, str]] = []

        # Input history for prompt toolkit
        self.input_history = InMemoryHistory()

        # Queue of proposals awaiting approval
        self.pending_proposals: List[Dict] = []

        # Counter for consecutive Ctrl-D presses (for exit confirmation)
        self.eof_count = 0

        # Style for prompt toolkit
        self.prompt_style = Style.from_dict({
            "prompt": "#00aa00 bold",
        })

    def add_system_context(self) -> None:
        """
        Add system context about the current project to the chat.

        This provides the AI with information about the project structure and files.
        """
        if not self.project_manager.is_project_loaded():
            return

        # Get project information
        project_info = self.project_manager.get_project_info()

        # Create a context message with instructions
        context = "You are an AI assistant helping with code development. "
        context += "When providing code, use markdown code blocks with the filename as the first comment.\n\n"
        context += "Example format:\n"
        context += "```python\n# main.py\nimport sys\nprint('Hello')\n```\n\n"
        context += "Current project information:\n"
        context += f"Path: {project_info.get('path', 'Unknown')}\n"
        context += f"Description: {project_info.get('description', 'No description')}\n"

        # Add file statistics
        if "statistics" in project_info:
            stats = project_info["statistics"]
            context += f"Total files: {stats.get('total_files', 0)}\n"
            context += f"Total lines: {stats.get('total_lines', 0)}\n"

        # Add file list
        file_list = self.project_manager.get_file_list()
        if file_list:
            context += "\nProject files:\n"
            for file_path in file_list[:20]:  # Limit to first 20 files
                context += f"  - {file_path}\n"
            if len(file_list) > 20:
                context += f"  ... and {len(file_list) - 20} more files\n"

        # Add as a system message
        self.chat_history.append({
            "role": "system",
            "content": context
        })

    def send_message(self, message: str) -> str:
        """
        Send a message to the AI and get a streaming response with visual feedback.

        Args:
            message: The user's message

        Returns:
            The AI's complete response
        """
        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": message
        })

        # Print assistant prefix
        print("\nAssistant: ", end="", flush=True)

        # Collect the full response while streaming
        full_response = ""

        try:
            # Stream the response from Ollama
            for chunk in self.ollama_client.chat_stream(self.chat_history):
                # Print each chunk as it arrives
                print(chunk, end="", flush=True)

                # Accumulate the full response
                full_response += chunk
        except Exception as e:
            error_msg = f"\nError during streaming: {e}"
            print(error_msg)
            full_response += error_msg

        # Print newline after response
        print("\n")

        # Add assistant response to history
        self.chat_history.append({
            "role": "assistant",
            "content": full_response
        })

        return full_response

    def parse_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Parse code blocks from markdown text, handling nested blocks correctly.

        Args:
            text: The text containing code blocks

        Returns:
            List of dictionaries with 'language', 'code', and optionally 'filename'
        """
        code_blocks = []

        # Use a state machine approach to handle nested code blocks
        i = 0
        while i < len(text):
            # Look for opening code block marker
            if text[i:i+3] == '```':
                # Find the end of the opening line to get the language
                line_end = text.find('\n', i)
                if line_end == -1:
                    break

                # Extract language specifier
                language = text[i+3:line_end].strip() or "text"

                # Start searching for the closing marker
                content_start = line_end + 1
                j = content_start

                # For markdown blocks, we need to handle nested code blocks
                if language in ['markdown', 'md']:
                    # Count nested code blocks
                    nesting_level = 0
                    while j < len(text):
                        # Look for ``` at start of line
                        if j == content_start or text[j-1] == '\n':
                            if text[j:j+3] == '```':
                                # Check if there's content after ``` (opening) or not (closing)
                                line_end_j = text.find('\n', j)
                                if line_end_j == -1:
                                    line_end_j = len(text)

                                # Get the content after ```
                                after_ticks = text[j+3:line_end_j].strip()

                                if after_ticks and after_ticks[0].isalpha():
                                    # This is an opening marker (has language)
                                    nesting_level += 1
                                    j = line_end_j + 1
                                elif nesting_level > 0:
                                    # This is a closing marker for a nested block
                                    nesting_level -= 1
                                    j = line_end_j + 1
                                else:
                                    # This is the closing marker for our markdown block
                                    code = text[content_start:j]
                                    code_blocks.append({
                                        "language": language,
                                        "code": code.strip(),
                                        "filename": None
                                    })
                                    i = j + 3
                                    break
                            else:
                                j += 1
                        else:
                            j += 1

                    if j >= len(text):
                        # No closing marker found, take rest of text
                        code = text[content_start:]
                        code_blocks.append({
                            "language": language,
                            "code": code.strip(),
                            "filename": None
                        })
                        break
                else:
                    # For non-markdown blocks, simple search for closing ```
                    closing = text.find('\n```', content_start)
                    if closing == -1:
                        closing = text.find('```', content_start)

                    if closing == -1:
                        # No closing marker, take rest of text
                        code = text[content_start:]
                        i = len(text)
                    else:
                        # Extract code between markers
                        code = text[content_start:closing]
                        i = closing + 4  # Skip past ```

                    # Try to extract filename from first comment line
                    filename = None
                    lines = code.split("\n")
                    if lines:
                        first_line = lines[0].strip()

                        # Check for comment with filename
                        if first_line.startswith("#") and ("." in first_line or "/" in first_line):
                            # Extract filename from comment
                            potential_filename = first_line.lstrip("#").strip()

                            # Check if it looks like a filename
                            if "/" in potential_filename or "." in potential_filename:
                                filename = potential_filename

                                # Remove the filename comment from code
                                code = "\n".join(lines[1:])

                    code_blocks.append({
                        "language": language,
                        "code": code.strip(),
                        "filename": filename
                    })
            else:
                i += 1

        return code_blocks

    def auto_create_files(self, response: str, user_message: str = "") -> int:
        """
        Automatically detect and propose file creation from AI response.

        Args:
            response: The AI's response text
            user_message: The user's original message (for context)

        Returns:
            Number of files proposed for creation
        """
        # Parse code blocks from the response
        code_blocks = self.parse_code_blocks(response)

        # Look for explicit file mentions in user message
        mentioned_files = self._extract_file_mentions(user_message)

        # Track number of files proposed
        files_proposed = 0

        # Process each code block
        for block in code_blocks:
            filename = block.get("filename")
            code = block.get("code")
            language = block.get("language")

            # If no filename detected but user mentioned a file, use that
            if not filename and mentioned_files and len(code_blocks) == 1:
                filename = mentioned_files[0]

            # For markdown blocks without filename, check if README is mentioned
            if not filename and language in ["markdown", "md"]:
                if mentioned_files:
                    filename = mentioned_files[0]
                elif "readme" in user_message.lower():
                    filename = "README.md"

            # Only create files if a filename was determined
            if filename and code:
                # Validate filename (no weird characters, must have extension or path separator)
                if self._is_valid_filename(filename):
                    # Check if file already exists
                    existing_content = self.project_manager.get_file_content(filename)

                    if existing_content:
                        # File exists, propose modification
                        self.propose_change(
                            filename,
                            f"Update {filename} with new code",
                            existing_content,
                            code
                        )
                    else:
                        # File doesn't exist, propose creation
                        self.propose_change(
                            filename,
                            f"Create new file {filename}",
                            "",
                            code
                        )

                    files_proposed += 1

        return files_proposed

    def _extract_file_mentions(self, text: str) -> List[str]:
        """
        Extract file mentions from text.

        Args:
            text: The text to search for file mentions

        Returns:
            List of potential filenames
        """
        # Pattern to match common filename patterns
        # Matches: README.md, main.py, src/app.js, etc.
        pattern = r'\b([a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*\.[a-zA-Z0-9]+)\b'
        matches = re.findall(pattern, text)

        return matches

    def _is_valid_filename(self, filename: str) -> bool:
        """
        Validate that a string looks like a reasonable filename.

        Args:
            filename: The filename to validate

        Returns:
            Boolean indicating if filename is valid
        """
        # Must have an extension or a path separator
        if "." not in filename and "/" not in filename:
            return False

        # Should not contain spaces (usually indicates it's not a filename)
        if " " in filename:
            return False

        # Should not be too long
        if len(filename) > 200:
            return False

        # Should not have weird characters
        invalid_chars = ["<", ">", "|", ":", "*", "?", '"']
        if any(char in filename for char in invalid_chars):
            return False

        return True

    def propose_change(self, file_path: str, description: str,
                      current_content: str, new_content: str) -> None:
        """
        Propose a change to a file for user review.

        Args:
            file_path: The relative path to the file to be modified
            description: A description of the proposed change
            current_content: The current file content
            new_content: The proposed new file content
        """
        # Add the proposal to the queue
        proposal = {
            "file_path": file_path,
            "description": description,
            "current_content": current_content,
            "new_content": new_content
        }
        self.pending_proposals.append(proposal)

        # Display the proposal to the user
        print("\n" + "=" * 70)
        print(f"PROPOSED CHANGE #{len(self.pending_proposals)}")
        print("=" * 70)
        print(f"File: {file_path}")
        print(f"Description: {description}")
        print("\nCurrent content preview:")
        print("-" * 70)
        print(current_content[:500])
        if len(current_content) > 500:
            print("... (truncated)")
        print("\nNew content preview:")
        print("-" * 70)
        print(new_content[:500])
        if len(new_content) > 500:
            print("... (truncated)")
        print("=" * 70)

    def approve_proposal(self) -> bool:
        """
        Apply all pending proposals if approved by the user.

        Returns:
            Boolean indicating whether all proposals were applied successfully
        """
        if not self.pending_proposals:
            print("No pending proposals to approve")
            return False

        # Track successes and failures
        successful_files = []
        failed_files = []

        # Process each proposal
        for proposal in self.pending_proposals:
            file_path = proposal["file_path"]
            new_content = proposal["new_content"]
            current_content = proposal["current_content"]
            description = proposal["description"]

            # Determine if this is a new file or an update
            is_new_file = not current_content

            # Apply the change
            if is_new_file:
                # Create new file (no backup needed)
                success = self.project_manager.file_editor.create_file(file_path, new_content)
                if not success:
                    # File might already exist, try write instead
                    success = self.project_manager.file_editor.write_file(file_path, new_content,
                                                                           create_backup=False)
            else:
                # Update existing file (with backup)
                success = self.project_manager.file_editor.write_file(file_path, new_content,
                                                                       create_backup=True)

            if success:
                action = "Created" if is_new_file else "Updated"
                print(f"{action} file: {file_path}")
                successful_files.append(file_path)
            else:
                print(f"Failed to apply change to {file_path}")
                failed_files.append(file_path)

        # Commit all successful changes together
        if successful_files:
            commit_message = f"Applied changes to {len(successful_files)} file(s)"
            self.project_manager.git_manager.commit_changes(commit_message, successful_files)

            # Rescan the project to pick up new files
            self.project_manager.file_scanner.scan_directory()

        # Clear all proposals
        self.pending_proposals = []

        # Return success if at least some files were created
        if successful_files:
            print(f"\nSuccessfully processed {len(successful_files)} file(s)")
            if failed_files:
                print(f"Failed to process {len(failed_files)} file(s): {', '.join(failed_files)}")
            return True
        else:
            print(f"Failed to process all {len(failed_files)} file(s)")
            return False

    def reject_proposal(self) -> None:
        """
        Reject all pending proposals without applying changes.
        """
        if not self.pending_proposals:
            print("No pending proposals to reject")
            return

        # Show what's being rejected
        file_count = len(self.pending_proposals)
        print(f"Rejected {file_count} proposed change(s):")
        for proposal in self.pending_proposals:
            print(f"  - {proposal['file_path']}")

        # Clear all proposals
        self.pending_proposals = []

    def process_user_input(self, user_input: str) -> str:
        """
        Process user input and handle special commands.

        Args:
            user_input: The user's input string

        Returns:
            Response message
        """
        # Strip whitespace
        user_input = user_input.strip()

        # Check for special commands
        if user_input.lower() == "/approve":
            if self.approve_proposal():
                return "Proposal approved and applied"
            else:
                return "Failed to approve proposal"

        elif user_input.lower() == "/reject":
            self.reject_proposal()
            return "Proposal rejected"

        elif user_input.lower() == "/status":
            return self._get_project_status()

        elif user_input.lower().startswith("/file "):
            file_path = user_input[6:].strip()
            return self._show_file_content(file_path)

        elif user_input.lower() == "/files":
            return self._list_files()

        elif user_input.lower() == "/history":
            return self._show_git_history()

        elif user_input.lower().startswith("/revert"):
            parts = user_input.split()
            if len(parts) > 1:
                commit_hash = parts[1]
                return self._revert_to_commit(commit_hash)
            else:
                return self._revert_last_change()

        elif user_input.lower() == "/help":
            return self._show_help()

        elif user_input.lower() in ["/quit", "/exit"]:
            return "QUIT"

        else:
            # Regular chat message
            response = self.send_message(user_input)

            # Check if the response contains code blocks with filenames
            files_proposed = self.auto_create_files(response, user_input)

            # If files were proposed, ask for immediate approval
            if files_proposed > 0:
                print(f"\n{'='*70}")
                print(f"Detected {files_proposed} file(s) in the response.")
                print(f"Press Enter to approve all changes, or type 'q' to reject: ", end="", flush=True)

                try:
                    user_response = input().strip().lower()
                    if user_response == "" or user_response == "y" or user_response == "yes":
                        # Approve changes
                        if self.approve_proposal():
                            return ""
                        else:
                            return "Failed to approve proposal"
                    else:
                        # Reject changes
                        self.reject_proposal()
                        return ""
                except (KeyboardInterrupt, EOFError):
                    print("\nRejecting changes...")
                    self.reject_proposal()
                    return ""

            return ""

    def _get_project_status(self) -> str:
        """
        Get the current project status.

        Returns:
            Status information as a string
        """
        if not self.project_manager.is_project_loaded():
            return "No project loaded"

        # Get project info
        info = self.project_manager.get_project_info()

        # Format the status message
        status = "Project Status:\n"
        status += f"Path: {info.get('path', 'Unknown')}\n"
        status += f"Description: {info.get('description', 'No description')}\n"

        if "statistics" in info:
            stats = info["statistics"]
            status += f"Files: {stats.get('total_files', 0)}\n"
            status += f"Lines: {stats.get('total_lines', 0)}\n"

        if "modified_files" in info and info["modified_files"]:
            status += f"\nModified files: {len(info['modified_files'])}\n"
            for file_path in info["modified_files"]:
                status += f"  - {file_path}\n"

        # Show pending proposals
        if self.pending_proposals:
            status += f"\nPending proposals: {len(self.pending_proposals)}\n"
            for proposal in self.pending_proposals:
                status += f"  - {proposal['file_path']}: {proposal['description']}\n"

        return status

    def _show_file_content(self, file_path: str) -> str:
        """
        Show the content of a specific file.

        Args:
            file_path: The relative path to the file

        Returns:
            The file content or error message
        """
        content = self.project_manager.get_file_content(file_path)

        if content:
            return f"Content of {file_path}:\n{content}"
        else:
            return f"Could not read file: {file_path}"

    def _list_files(self) -> str:
        """
        List all files in the project.

        Returns:
            List of files as a string
        """
        files = self.project_manager.get_file_list()

        if not files:
            return "No files found in project"

        result = "Project files:\n"
        for file_path in files:
            result += f"  - {file_path}\n"

        return result

    def _show_git_history(self) -> str:
        """
        Show the git commit history.

        Returns:
            Commit history as a string
        """
        if not self.project_manager.git_manager:
            return "No git repository available"

        history = self.project_manager.git_manager.get_commit_history(10)

        if not history:
            return "No commit history available"

        result = "Recent commits:\n"
        for commit in history:
            result += f"  {commit}\n"

        return result

    def _revert_to_commit(self, commit_hash: str) -> str:
        """
        Revert to a specific commit.

        Args:
            commit_hash: The hash of the commit to revert to

        Returns:
            Result message
        """
        if self.project_manager.revert_changes(commit_hash):
            return f"Reverted to commit {commit_hash}"
        else:
            return f"Failed to revert to commit {commit_hash}"

    def _revert_last_change(self) -> str:
        """
        Revert the last change.

        Returns:
            Result message
        """
        if self.project_manager.revert_changes():
            return "Reverted last change"
        else:
            return "Failed to revert last change"

    def _show_help(self) -> str:
        """
        Show help information about available commands.

        Returns:
            Help text
        """
        help_text = """
Available commands:
  /approve     - Approve and apply any pending proposals (if using manual mode)
  /reject      - Reject any pending proposals (if using manual mode)
  /status      - Show project status
  /file <path> - Show content of a specific file
  /files       - List all files in the project
  /history     - Show git commit history
  /revert      - Revert the last change
  /revert <hash> - Revert to a specific commit
  /help        - Show this help message
  /quit, /exit - Exit the chat interface

Exit options:
  - Type /quit or /exit to exit immediately
  - Press Ctrl+D twice consecutively to exit
  - Press Ctrl+C to cancel current input (does not exit)

Conversation mode:
  - Have natural conversations with the AI about your code
  - When the AI provides code with filenames, you'll be prompted:
    Press Enter to approve all changes, or type 'q' to reject
"""
        return help_text

    def run(self) -> None:
        """
        Run the interactive chat interface.

        This is the main loop that processes user input and displays responses.
        """
        print("\n" + "=" * 70)
        print("Code Assistant Chat Interface")
        print("=" * 70)
        print("Type /help for available commands")
        print("Press Ctrl+D twice or type /quit to exit")
        print("=" * 70 + "\n")

        # Add system context to the chat
        self.add_system_context()

        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = prompt(
                    [("class:prompt", "You: ")],
                    style=self.prompt_style,
                    history=self.input_history
                )

                # Reset EOF counter when user successfully enters input
                self.eof_count = 0

                # Process the input
                response = self.process_user_input(user_input)

                # Check if user wants to quit
                if response == "QUIT":
                    print("Goodbye!")
                    break

                # Display the response (only if not empty)
                # For regular chat messages, response is already streamed
                if response:
                    print(f"\n{response}\n")

            except KeyboardInterrupt:
                # Handle Ctrl+C
                print("\nUse /quit to exit")
                # Reset EOF counter on interrupt
                self.eof_count = 0
                continue
            except EOFError:
                # Handle Ctrl+D (requires two consecutive presses to exit)
                self.eof_count += 1

                if self.eof_count == 1:
                    # First Ctrl+D press
                    print("\n(Press Ctrl+D again to exit, or continue typing)")
                    continue
                else:
                    # Second consecutive Ctrl+D press
                    print("\nGoodbye!")
                    break
