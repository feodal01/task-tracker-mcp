# task-tracker-mcp

## Description
`task-tracker-mcp` is a task management system for LLM-based agents. All tasks are stored in a single tree, available immediately after the server starts.

## Main Goal
Enable LLM agents to manage their tasks through a unified Task manager.

## Requirements
- Python 3.13 or higher
- Node.js and npm (for @modelcontextprotocol/inspector)

## Installation

### Cloning the Repository
```bash
git clone git@github.com:feodal01/task-tracker-mcp.git
cd task-tracker-mcp
```

### Setting Up the Environment

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
        "mcp_server.mcp_service"
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
export PYTHONPATH=/Path/to/task-tracker-mcp/src
uv run python -m src.mcp_server.mcp_service
```

### Starting the Inspector
To inspect the MCP server, use:
**uv:**
```bash
npx @modelcontextprotocol/inspector uv --directory /Path/to/task-tracker-mcp run python -m mcp_server.mcp_service 
```

## Running Tests

**uv:**
```bash
export PYTHONPATH=/Path/to/task-tracker-mcp/src
uv run pytest tests/
```

## Running FastApi service with MCP tools

```bash
export PYTHONPATH=/Path/to/task-tracker-mcp/src
uv --directory /Path/to/task-tracker-mcp run python -m mcp_server.mcp_rest_service
```

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contribution
Want to contribute? Fork the repository and submit a pull request.

## Contacts
If you have any questions, contact me at: evgenyorlov1991@gmail.com
