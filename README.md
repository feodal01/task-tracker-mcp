# task-tracker-mcp

## Description
`task-tracker-mcp` is a task management system for LLM-based agents. All tasks are stored in a single tree, available immediately after the server starts.

## Main Goal
Enable LLM agents to manage their tasks through a unified Task manager.

## Requirements
- Python 3.13 or higher
- Node.js and npm

## Installation

### Cloning the Repository
```bash
git clone https://github.com/your_username/task-tracker-mcp.git
cd task-tracker-mcp
```

### Setting Up the Environment

#### Using uv (Recommended)

1. Install [uv](https://github.com/astral-sh/uv):
   ```bash
   pip install uv
   ```
2. Install requirements:
   ```bash
   uv pip install -r requirements.txt
   ```

#### Using Pipenv
Create a virtual environment and install dependencies:
```bash
pipenv install
pipenv shell
```

## Configuration
Open the Claude Desktop configuration file located at:

On macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
On Windows: %APPDATA%/Claude/claude_desktop_config.json
Add the following:
```json
{
  "mcpServers": {
    "mcpServer": {
      "command": "uv",
      "args": [
        "--directory", 
        "/Path/to/task-tracker-mcp", 
        "run",
        "python",
        "-m",
        "mcp_server.main"
      ],
      "env": {
        "PYTHONPATH": "/Path/to/task-tracker-mcp/src"
      }
    }
  }
}
```

## Running the Project

### Starting the MCP Server

**Using uv:**
```bash
uv pip install -r requirements.txt
uv python -m src.mcp_server.main
```

### Starting the Inspector
To inspect the MCP server, use:

**pipenv:**
```bash
export PYTHONPATH=src
npx @modelcontextprotocol/inspector pipenv run python -m src.mcp_server.main
```

**uv:**
```bash
npx @modelcontextprotocol/inspector uv --directory /Path/to/task-tracker-mcp run python -m mcp_server.main 
```

## Running Tests

**uv:**
```bash
uv pip install -r requirements.txt
export PYTHONPATH=src
uv pytest tests/
```

**pipenv:**
```bash
export PYTHONPATH=src
pytest tests/test_database.py
```

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contribution
Want to contribute? Fork the repository and submit a pull request.

## Contacts
If you have any questions, contact me at: evgenyorlov1991@gmail.com