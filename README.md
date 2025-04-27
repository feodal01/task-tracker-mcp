# task-tracker-mcp

## Description
`task-tracker-mcp` is a task management system for LLM-based agents. All tasks are stored in a single tree, available immediately after the server starts.

## Main Goal
Enable LLM agents to manage their tasks through a unified Task manager.

## Requirements
- Python 3.8 or higher
- Node.js and npm
- MongoDB

## Installation

### Cloning the Repository
```bash
git clone https://github.com/your_username/task-tracker-mcp.git
cd task-tracker-mcp
```

### Setting Up the Environment
Create a virtual environment and install dependencies:
```bash
pipenv install
```

### Docker
1. **Install Docker**: Follow the instructions on the [Docker installation page](https://docs.docker.com/get-docker/) for your operating system.
2. **Build and run the containers**:
   ```bash
   docker-compose up --build
   ```

## Running the Project

### Starting the MCP Server
To run the MCP server, use:
```bash
export PYTHONPATH=src
pipenv run python -m src.mcp_server.main
```

### Starting the Inspector
To inspect the MCP server, use:
```bash
export PYTHONPATH=src
npx @modelcontextprotocol/inspector pipenv run python -m src.mcp_server.main
```

## Running Tests
To run the tests, use:
```bash
export PYTHONPATH=src
pytest tests/test_database.py
```

## Usage
After starting the server, all commands work with tasks inside a single task tree. There is no need to specify a tree identifier — just create, update, delete, and retrieve tasks directly.

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contribution
Want to contribute? Fork the repository and submit a pull request.

## Contacts
If you have any questions, contact the author at: your_email@example.com