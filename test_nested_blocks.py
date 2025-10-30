#!/usr/bin/env python3
"""
Test script to verify nested code block parsing
"""

from chat_interface import ChatInterface
from ollama_client import OllamaClient
from project_manager import ProjectManager
import tempfile
import shutil


def test_nested_markdown_blocks():
    """
    Test parsing of markdown blocks containing nested code blocks.
    """
    # Create a temporary project
    temp_dir = tempfile.mkdtemp()

    try:
        # Initialize components
        ollama_client = OllamaClient()
        project_manager = ProjectManager()
        project_manager.load_existing_project(temp_dir)

        chat_interface = ChatInterface(ollama_client, project_manager)

        # Test case: markdown block with nested bash blocks
        test_text = """```markdown
# README
This is a readme file.

## Installation
```bash
pip install requests
```

## Usage
```bash
python main.py
```

## More info
Some more content here.
```"""

        print("Testing nested code block parsing:")
        print("=" * 70)
        print("Input text:")
        print(test_text)
        print("\n" + "=" * 70)

        # Parse the blocks
        blocks = chat_interface.parse_code_blocks(test_text)

        print(f"\nFound {len(blocks)} code block(s):")
        for i, block in enumerate(blocks):
            print(f"\n--- Block {i+1} ---")
            print(f"Language: {block['language']}")
            print(f"Filename: {block.get('filename', 'None')}")
            print(f"Content length: {len(block['code'])} characters")
            print(f"Content preview (first 200 chars):")
            print(block['code'][:200])
            if len(block['code']) > 200:
                print("...")
            print(f"Content preview (last 100 chars):")
            print("..." + block['code'][-100:])

        # Verify we got the full content
        if len(blocks) == 1:
            content = blocks[0]['code']
            # Check that it contains all the expected sections
            has_readme = '# README' in content
            has_installation = '## Installation' in content
            has_usage = '## Usage' in content
            has_more_info = '## More info' in content
            has_nested_bash_1 = '```bash' in content
            has_nested_bash_2 = content.count('```bash') == 2

            print("\n" + "=" * 70)
            print("Validation:")
            print(f"  Contains '# README': {has_readme}")
            print(f"  Contains '## Installation': {has_installation}")
            print(f"  Contains '## Usage': {has_usage}")
            print(f"  Contains '## More info': {has_more_info}")
            print(f"  Contains nested bash blocks: {has_nested_bash_1}")
            print(f"  Has exactly 2 bash blocks: {has_nested_bash_2}")

            if all([has_readme, has_installation, has_usage, has_more_info, has_nested_bash_2]):
                print("\n  PASS: All content correctly captured!")
            else:
                print("\n  FAIL: Content is incomplete!")
        else:
            print(f"\nFAIL: Expected 1 block, got {len(blocks)}")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_simple_python_block():
    """
    Test parsing of simple Python blocks.
    """
    # Create a temporary project
    temp_dir = tempfile.mkdtemp()

    try:
        # Initialize components
        ollama_client = OllamaClient()
        project_manager = ProjectManager()
        project_manager.load_existing_project(temp_dir)

        chat_interface = ChatInterface(ollama_client, project_manager)

        # Test case: simple Python block with filename
        test_text = """```python
# main.py
def hello():
    print("Hello, world!")

if __name__ == "__main__":
    hello()
```"""

        print("\n" + "=" * 70)
        print("Testing simple Python block with filename:")
        print("=" * 70)

        # Parse the blocks
        blocks = chat_interface.parse_code_blocks(test_text)

        print(f"\nFound {len(blocks)} code block(s):")
        for i, block in enumerate(blocks):
            print(f"\n--- Block {i+1} ---")
            print(f"Language: {block['language']}")
            print(f"Filename: {block.get('filename', 'None')}")
            print(f"Content:")
            print(block['code'])

        # Verify
        if len(blocks) == 1 and blocks[0].get('filename') == 'main.py':
            print("\n  PASS: Correctly extracted filename and content!")
        else:
            print("\n  FAIL: Filename extraction failed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("=" * 70)
    print("Nested Code Block Parsing Test Suite")
    print("=" * 70)

    test_nested_markdown_blocks()
    test_simple_python_block()

    print("\n" + "=" * 70)
    print("Tests complete!")
    print("=" * 70)
