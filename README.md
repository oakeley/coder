# Code Assistant

A comprehensive AI-powered code management and development tool that leverages a local Ollama qwen3-coder:30b model to understand, analyze, edit, and maintain software projects. With a full 128K token context window, Code Assistant can process and comprehend entire codebases while providing real-time assistance through an interactive chat interface.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Usage Guide](#detailed-usage-guide)
- [Command Reference](#command-reference)
- [Features In-Depth](#features-in-depth)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Safety and Security](#safety-and-security)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

### What is Code Assistant?

Code Assistant is an intelligent development companion that combines the power of large language models with robust project management capabilities. Unlike traditional code completion tools, Code Assistant maintains full context of your entire project and engages in natural conversation to help you:

- **Understand complex codebases** - Ask questions about how code works and receive detailed explanations
- **Develop new features** - Describe what you want to build and let the AI generate complete, working implementations
- **Debug and fix issues** - Report problems and get intelligent suggestions with automatic code fixes
- **Refactor and improve code** - Request improvements and watch as the AI proposes cleaner, more efficient solutions
- **Maintain project history** - Every change is tracked with git, allowing easy reversion if needed

### Why Use Code Assistant?

**Traditional IDEs with AI assistants:**
- Limited context window (8-16K tokens)
- Line-by-line suggestions without project understanding
- No conversation or clarification
- Manual file management

**Code Assistant:**
- Massive 128K token context (entire small-to-medium projects)
- Understands relationships between files and modules
- Natural conversation with follow-up questions
- Automatic file creation and modification with approval workflow
- Complete git integration for safe experimentation
- Real-time streaming responses for immediate feedback

---

## Key Features

### Core Capabilities

**AI-Powered Development**
- Natural Language Interface - Describe what you want in plain English
- Full Project Context - 128K tokens means understanding your entire codebase
- Streaming Responses - See the AI thinking in real-time
- Smart Code Generation - Creates complete, working implementations

**File Management**
- Automatic File Creation - AI generates files from code blocks
- Safe Editing - All changes require approval before application
- Automatic Backups - Timestamped backups before every modification
- Intelligent Filename Detection - Extracts filenames from your messages

**Version Control**
- Git Integration - Automatic commits with descriptive messages
- Easy Reversion - Undo changes with simple commands
- Change History - View complete project evolution
- Safe Experimentation - Try ideas without fear of breaking things

**Project Understanding**
- Automatic Scanning - Discovers all source files in your project
- Multi-Language Support - 20+ programming languages recognized
- Project Statistics - File counts, line counts, structure analysis
- Smart Search - Find files by pattern or content

**User Experience**
- Interactive Chat - Natural conversation with the AI
- Command System - Quick actions via slash commands
- Clean Interface - ASCII-only output, no distracting symbols
- Fast Approval - Press Enter to accept, 'q' to reject

---

## System Requirements

### Required Software

**Operating System:**
- Linux (tested on Ubuntu 20.04+)
- macOS (10.15+)
- Windows 10/11 with WSL2

**Python:**
- Python 3.8 or higher
- pip package manager

**Git:**
- Git 2.20 or higher

**Ollama:**
- Ollama runtime
- qwen3-coder:30b model (approximately 17GB download)

### Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 16GB
- Disk: 25GB free space
- Internet: For initial model download

**Recommended:**
- CPU: 8+ cores
- RAM: 32GB
- Disk: 50GB free space (SSD preferred)
- GPU: Optional, but improves response time

---

## Installation

### Step 1: Install Prerequisites

#### Install Python

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.8 python3-pip git
```

**macOS:**
```bash
brew install python@3.8 git
```

**Windows (WSL2):**
```bash
sudo apt update
sudo apt install python3.8 python3-pip git
```

#### Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from https://ollama.ai/download and follow installer instructions.

**Verify installation:**
```bash
ollama --version
```

### Step 2: Install Ollama Model

Download the qwen3-coder:30b model (this may take 15-30 minutes):

```bash
ollama pull qwen3-coder:30b
```

**Verify model installation:**
```bash
ollama list
```

You should see `qwen3-coder:30b` in the list.

### Step 3: Start Ollama Server

**Option A - Run in foreground:**
```bash
ollama serve
```

**Option B - Run as background service:**

**Linux (systemd):**
```bash
sudo systemctl start ollama
sudo systemctl enable ollama  # Start on boot
```

**macOS:**
```bash
brew services start ollama
```

**Verify server is running:**
```bash
curl http://localhost:11434/api/tags
```

### Step 4: Install Code Assistant

**Clone the repository:**
```bash
git clone <repository-url>
cd coder
```

**Or download the files directly if not using git.**

**Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed requests-2.31.0 ollama-0.1.0 gitpython-3.1.40 prompt-toolkit-3.0.43
```

### Step 5: Verify Installation

Run the test suite:
```bash
python run_tests.py
```

All 39 tests should pass:
```
======================================================================
All tests passed successfully!
======================================================================
```

---

## Quick Start

### First Launch

Start Code Assistant:
```bash
python main.py
```

### Initial Setup

You'll see a welcome screen:
```
======================================================================
Code Assistant - AI-Powered Code Management Tool
======================================================================
Using Ollama qwen3-coder:30b with 128K token context
======================================================================

Testing connection to Ollama API...
Successfully connected to Ollama API

Project Setup
----------------------------------------------------------------------
Would you like to create a new project? (yes/no):
```

**Option 1: Create a New Project**

Type `yes` and press Enter:
```
Would you like to create a new project? (yes/no): yes

Creating New Project
----------------------------------------------------------------------
Enter project path (default: /current/directory/my_project): /home/user/my_calculator
Description: A scientific calculator with advanced functions

Creating project at: /home/user/my_calculator
Project created successfully!
Project initialized with git repository
```

**Option 2: Use Existing Project**

Type `no` and press Enter:
```
Would you like to create a new project? (yes/no): no

Loading Existing Project
----------------------------------------------------------------------
Enter project path (default: current directory): /home/user/existing_project

Loading project from: /home/user/existing_project
Found 15 source files
Total lines of code: 1,234
Git repository detected
Project loaded successfully!
```

### Your First Interaction

After setup, you'll see the chat interface:
```
======================================================================
Code Assistant Chat Interface
======================================================================
Type /help for available commands
Press Ctrl+D twice or type /quit to exit
======================================================================

You:
```

**Example conversation:**
```
You: Please create a simple Python calculator that can add, subtract, multiply, and divide