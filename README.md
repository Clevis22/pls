# pls

A command-line tool that uses AI to generate and execute terminal commands from natural language descriptions.

## Overview

`pls` is a macOS terminal assistant powered by local AI (via Ollama) that translates your plain English requests into executable shell commands. It can also answer technical questions about macOS in a conversational mode.

## Features

- 🤖 **Natural Language to Commands**: Describe what you want to do, get the exact command
- 💬 **Ask Mode**: Get technical answers and explanations with the `-a` flag
- ⚡ **Smart Ollama Management**: Automatically starts/stops Ollama server as needed
- 🎨 **Beautiful Terminal UI**: Rich formatting with syntax highlighting and interactive prompts
- 🔒 **Safety First**: Always shows the command and asks for confirmation before execution

## Requirements

- Python 3.x
- macOS
- [Ollama](https://ollama.ai) installed
- `ministral-3:8b` model pulled (`ollama pull ministral-3:8b`)

### Python Dependencies

```bash
pip install ollama rich requests
```

## Installation

1. Clone or download the script
2. Make it executable:
   ```bash
   chmod +x pls
   ```
3. (Optional) Move to your PATH:
   ```bash
   sudo mv pls /usr/local/bin/
   ```

## Usage

### Command Mode (Default)

Generate and execute commands from natural language:

```bash
pls "find all python files in current directory"
pls "compress Documents folder"
pls "show disk usage"
```

The tool will:
1. Generate the appropriate command
2. Display it with syntax highlighting
3. Ask for confirmation before running

### Ask Mode (`-a`)

Get answers to technical questions:

```bash
pls -a "how do I change file permissions?"
pls -a "what's the difference between chmod and chown?"
pls -a "explain the find command"
```

## How It Works

1. **Ollama Detection**: Checks if Ollama server is running
2. **Auto-Start**: Starts Ollama automatically if needed (with a neat loading animation)
3. **AI Processing**: Sends your query to the `ministral-3:8b` model
4. **Smart Output**: 
   - Command mode: Shows executable command with confirmation prompt
   - Ask mode: Displays helpful answer in a formatted panel
5. **Cleanup**: Shuts down Ollama if it wasn't running before (saves resources)

## Configuration

Edit these variables at the top of the script to customize:

```python
MODEL = "ministral-3:8b"              # Change AI model
OLLAMA_API_URL = "http://127.0.0.1:11434"  # Change Ollama endpoint
```

## Examples

```bash
# Find large files
pls "find files larger than 100MB"

# Git operations
pls "create a new git branch called feature-x"

# System info
pls "show CPU temperature"

# Ask for help
pls -a "how do I monitor network traffic?"
```

## Safety Features

- Commands are **always shown before execution**
- User confirmation required (Y/n prompt)
- Graceful interrupt handling (Ctrl+C)
- Automatic cleanup of zombie processes

## Troubleshooting

**Ollama won't start:**
- Ensure Ollama is installed: `brew install ollama`
- Check if the model is available: `ollama list`

**Model not found:**
```bash
ollama pull ministral-3:8b
```

**Permission errors:**
- Make sure the script is executable: `chmod +x pls`

## License

This is a utility script provided as-is. Modify and use freely under the MIT license.

## Contributing

Feel free to fork and customize for your needs! Some ideas:
- Add support for other AI models
- Implement command history
- Add shell completion
- Support for other operating systems

---

**Note**: This tool executes commands on your system. Always review generated commands before confirming execution.
