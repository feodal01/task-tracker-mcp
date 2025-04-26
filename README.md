# task-tracker-mcp

## Description
`task-tracker-mcp` is a project that allows LLM-based agents to manage their tasks using a task management system.

## Main Goal
To enable LLM agents to manage their tasks by running the `Task manager`.

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
2. **Build and Run the Docker Containers**: Use the following command to build and run the application along with MongoDB:
   ```bash
   docker-compose up --build
   ```

## Running the Project

### Starting the Server
To run the MCP server, use the following command:
```bash
pipenv run python -m src.mcp_server.main
```

### Starting the Inspector
To start inspecting the MCP server, use `mcpinspector`:
```bash
npx @modelcontextprotocol/inspector pipenv run python -m src.mcp_server.main
```

## Usage
After starting the server, you can interact with it via standard input/output or using an MCP client.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contribution
If you would like to contribute, please fork the repository and submit a pull request.

## Contacts
If you have any questions, you can reach the author at: your_email@example.com