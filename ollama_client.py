"""
Ollama Client Wrapper Module

This module provides a wrapper for interacting with the local Ollama API,
specifically configured for the qwen3-coder:30b model with full 128K token context.
"""

import requests
import json
from typing import List, Dict, Optional


class OllamaClient:
    """
    A client wrapper for communicating with the local Ollama API.

    This class handles all interactions with the qwen3-coder:30b model,
    ensuring that the full 128K token context window is utilised.
    """

    def __init__(self, model_name: str = "qwen3-coder:30b", base_url: str = "http://localhost:11434"):
        """
        Initialise the Ollama client.

        Args:
            model_name: The name of the Ollama model to use
            base_url: The base URL for the Ollama API server
        """
        # Store the model name for all API calls
        self.model_name = model_name

        # Store the base URL for the Ollama API
        self.base_url = base_url

        # API endpoint for generating responses
        self.generate_endpoint = f"{base_url}/api/generate"

        # API endpoint for chat-based interactions
        self.chat_endpoint = f"{base_url}/api/chat"

        # Maximum context length for qwen3-coder:30b (128K tokens)
        self.context_length = 131072

    def test_connection(self) -> bool:
        """
        Test the connection to the Ollama API server.

        Returns:
            Boolean indicating whether the connection is successful
        """
        try:
            # Attempt to connect to the API server
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)

            # Check if the request was successful
            return response.status_code == 200
        except Exception as e:
            # Connection failed
            print(f"Connection test failed: {e}")
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, stream: bool = False) -> str:
        """
        Generate a response from the model using the generate endpoint.

        Args:
            prompt: The user prompt to send to the model
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness in generation (0.0 to 1.0)
            stream: Whether to stream the response

        Returns:
            The generated response text
        """
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                # Set the context length to maximum (128K tokens)
                "num_ctx": self.context_length,
                # Control the randomness of the output
                "temperature": temperature
            }
        }

        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        try:
            # Send the request to the API
            response = requests.post(self.generate_endpoint, json=payload, timeout=300)

            # Check for successful response
            if response.status_code == 200:
                # Parse the response JSON
                result = response.json()
                return result.get("response", "")
            else:
                # Return error message if request failed
                return f"Error: API returned status code {response.status_code}"
        except Exception as e:
            # Return exception message if request failed
            return f"Error generating response: {e}"

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
             stream: bool = False) -> str:
        """
        Have a chat conversation with the model using the chat endpoint.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness in generation (0.0 to 1.0)
            stream: Whether to stream the response

        Returns:
            The assistant's response text
        """
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "options": {
                # Set the context length to maximum (128K tokens)
                "num_ctx": self.context_length,
                # Control the randomness of the output
                "temperature": temperature
            }
        }

        try:
            # Send the request to the API
            response = requests.post(self.chat_endpoint, json=payload, timeout=300)

            # Check for successful response
            if response.status_code == 200:
                # Parse the response JSON
                result = response.json()

                # Extract the assistant's message
                message = result.get("message", {})
                return message.get("content", "")
            else:
                # Return error message if request failed
                return f"Error: API returned status code {response.status_code}"
        except Exception as e:
            # Return exception message if request failed
            return f"Error in chat: {e}"

    def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7):
        """
        Have a chat conversation with streaming responses.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness in generation (0.0 to 1.0)

        Yields:
            Chunks of the response text as they are generated
        """
        # Prepare the request payload with streaming enabled
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {
                # Set the context length to maximum (128K tokens)
                "num_ctx": self.context_length,
                # Control the randomness of the output
                "temperature": temperature
            }
        }

        try:
            # Send the request to the API with streaming
            response = requests.post(self.chat_endpoint, json=payload,
                                    timeout=300, stream=True)

            # Check for successful response
            if response.status_code == 200:
                # Process the streaming response line by line
                for line in response.iter_lines():
                    if line:
                        # Parse each JSON line
                        try:
                            chunk = json.loads(line)

                            # Extract the content from the message
                            message = chunk.get("message", {})
                            content = message.get("content", "")

                            # Yield the content chunk
                            if content:
                                yield content

                            # Check if this is the final chunk
                            if chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
            else:
                # Yield error message if request failed
                yield f"Error: API returned status code {response.status_code}"
        except Exception as e:
            # Yield exception message if request failed
            yield f"Error in chat: {e}"

    def analyze_code(self, code: str, file_path: str) -> str:
        """
        Analyze code and provide insights about its structure and purpose.

        Args:
            code: The source code to analyze
            file_path: The path to the file being analyzed

        Returns:
            Analysis results as text
        """
        # Create a prompt for code analysis
        prompt = f"""Analyze the following code from file '{file_path}':

```
{code}
```

Provide a concise analysis including:
1. Purpose of the code
2. Key functions and classes
3. Dependencies and imports
4. Potential issues or improvements
"""

        # Use the generate endpoint for code analysis
        return self.generate(prompt, system_prompt="You are an expert code analyst.")

    def suggest_edit(self, code: str, file_path: str, instruction: str) -> str:
        """
        Suggest an edit to code based on user instruction.

        Args:
            code: The current source code
            file_path: The path to the file
            instruction: The user's instruction for editing

        Returns:
            Suggested code changes
        """
        # Create a prompt for code editing
        prompt = f"""Given the following code from file '{file_path}':

```
{code}
```

User instruction: {instruction}

Provide the modified code that implements this instruction. Only output the complete modified code, no explanations.
"""

        # Use the generate endpoint for code editing suggestions
        return self.generate(prompt, system_prompt="You are an expert programmer who makes precise code edits.")
