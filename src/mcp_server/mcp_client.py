#!/usr/bin/env python3
"""
MCP client for testing MCP server tools.
Allows calling various tools from the command line and
processing responses from language models (LLM).
"""

import argparse
import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, Field


from task_tracker.schemas import (
    CreateTaskParams,
    UpdateTaskParams,
    UpdateStatusParams,
    CloseTaskParams,
    DeleteTaskParams,
    GetTaskParams, Empty
)


# --- Example of a local tool ---
class SearchFileParams(BaseModel):
    query: str = Field(..., description="Search query")
    path: str = Field(..., description="Path for search")

def search_file(query: str, path: str):
    # Example of a simple local function
    return f"Local search: found match for '{query}' in '{path}'"

# --- Universal tool registry ---
TOOL_REGISTRY = {
    "create_task": {"type": "mcp", "schema": CreateTaskParams},
    "update_task": {"type": "mcp", "schema": UpdateTaskParams},
    "update_status": {"type": "mcp", "schema": UpdateStatusParams},
    "close_task": {"type": "mcp", "schema": CloseTaskParams},
    "delete_task": {"type": "mcp", "schema": DeleteTaskParams},
    "get_task": {"type": "mcp", "schema": GetTaskParams},
    "search_file": {"type": "local", "schema": SearchFileParams},
    "list_tasks": {"type": "mcp", "schema": Empty},
    "test_tool": {"type": "mcp", "schema": Empty}
}

# --- Universal handler for LLM call ---
class LLMToolCall(BaseModel):
    tool_name: str
    parameters: dict

async def handle_llm_tool_call(llm_json, session=None):
    call = LLMToolCall(**llm_json)
    tool_info = TOOL_REGISTRY.get(call.tool_name)
    if not tool_info:
        print(f"Unknown tool: {call.tool_name}")
        return None

    if schema := tool_info["schema"]:
        validated = schema(**call.parameters)
    else:
        validated = Empty

    if tool_info["type"] == "mcp":
        if session is None:
            raise RuntimeError("Active session required for MCP tools!")
        result = await session.call_tool(call.tool_name, arguments=validated.model_dump(exclude_none=True))
        print(f"MCP tool result '{call.tool_name}': {result}")
        return result
    elif tool_info["type"] == "local":
        result = search_file(**validated.model_dump(exclude_none=True))
        print(f"Local tool result '{call.tool_name}': {result}")
        return result

# --- Main async function ---
async def main():
    project_root = str(Path(__file__).parent.parent.parent.absolute())

    parser = argparse.ArgumentParser(description="Minimal MCP-client with Pydantic schemas and local tools support")
    parser.add_argument("--command", default="uv", help="Command to start MCP-server (default: uv)")
    parser.add_argument("--args", nargs="*",
                        default=["--directory", project_root, "run", "python", "-m", "mcp_server.mcp_service_lowlevel"],
                        help="Arguments for running MCP-server")
    parser.add_argument("--env", default=f"{project_root}/src", help="PYTHONPATH for server")
    args = parser.parse_args()

    server_params = StdioServerParameters(
        command=args.command,
        args=args.args,
        env={"PYTHONPATH": args.env}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Available MCP tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            print("\nAvailable local tools:")
            for name, info in TOOL_REGISTRY.items():
                if info["type"] == "local":
                    print(f"- {name}")

            # Example of calling an MCP tool through the universal handler
            llm_json_mcp = {
                "tool_name": "create_task",
                "parameters": {
                    "description": "Task through universal handler",
                    "dod": "Appeared in the task list"
                }
            }
            await handle_llm_tool_call(llm_json_mcp, session)

            llm_json_mcp = {
                "tool_name": "list_tasks",
                "parameters": {}
            }
            await handle_llm_tool_call(llm_json_mcp, session)

            # Example of calling a local tool through the universal handler
            llm_json_local = {
                "tool_name": "search_file",
                "parameters": {
                    "query": "process_llm_response",
                    "path": "./src/mcp_server"
                }
            }
            await handle_llm_tool_call(llm_json_local)

if __name__ == "__main__":
    asyncio.run(main()) 