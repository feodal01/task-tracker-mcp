from datetime import datetime
from typing import Any, Sequence

from mcp.server import FastMCP
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from task_tracker.database import InMemoryDatabase
from task_tracker.schemas import (
    TaskStatus, CreateTaskParams, UpdateTaskParams,
    UpdateStatusParams, DeleteTaskParams, GetTaskParams
)

app = Server("task-tracker-mcp-lowlevel")

db = InMemoryDatabase()

CREATE_TASK_SCHEMA = CreateTaskParams.model_json_schema()
UPDATE_TASK_SCHEMA = UpdateTaskParams.model_json_schema()
UPDATE_STATUS_SCHEMA = UpdateStatusParams.model_json_schema()
DELETE_TASK_SCHEMA = DeleteTaskParams.model_json_schema()
GET_TASK_SCHEMA = GetTaskParams.model_json_schema()
EMPTY_SCHEMA = {
    "type": "object",
    "properties": {},
    "required": []
}


async def create_task_lowlevel(**kwargs):
    try:
        params = CreateTaskParams(**kwargs)
        deadline = params.deadline
        if isinstance(deadline, str) and deadline:
            try:
                deadline = datetime.fromisoformat(deadline)
            except Exception:
                deadline = None
        parent_id = params.parent_id or db.tree.root.id
        task_id = await db.create_task(parent_id, params.description, params.dod, deadline=deadline, assignee=params.assignee)
        result = f"Task created with ID: {task_id}"
        return [types.TextContent(type="text", text=result)]
    except Exception as error:
        return [types.TextContent(type="text", text=f"Error: {str(error)}")]

async def update_task_lowlevel(**kwargs):
    try:
        params = UpdateTaskParams(**kwargs)
        deadline = params.deadline
        if isinstance(deadline, str) and deadline:
            try:
                deadline = datetime.fromisoformat(deadline)
            except Exception:
                deadline = None
        await db.update_task(
            params.task_id,
            description=params.description,
            dod=params.dod,
            deadline=deadline,
            assignee=params.assignee,
        )
        result = f"Task {params.task_id} updated"
        return [types.TextContent(type="text", text=result)]
    except Exception as error:
        return [types.TextContent(type="text", text=f"Error: {str(error)}")]

async def update_status_lowlevel(**kwargs):
    try:
        params = UpdateStatusParams(**kwargs)
        await db.update_task(
            params.task_id,
            status=TaskStatus(params.status),
            close_reason=params.reason
        )
        result = f"Task {params.task_id} status updated to {params.status}"
        return [types.TextContent(type="text", text=result)]
    except Exception as error:
        return [types.TextContent(type="text", text=f"Error: {str(error)}")]

async def delete_task_lowlevel(**kwargs):
    try:
        params = DeleteTaskParams(**kwargs)
        await db.delete_task(params.task_id)
        result = f"Task {params.task_id} deleted"
        return [types.TextContent(type="text", text=result)]
    except Exception as error:
        return [types.TextContent(type="text", text=f"Error: {str(error)}")]

async def get_task_lowlevel(**kwargs):
    try:
        params = GetTaskParams(**kwargs)
        task = await db.get_task(params.task_id)
        result = str(task)
        return [types.TextContent(type="text", text=result)]
    except Exception as error:
        return [types.TextContent(type="text", text=f"Error: {str(error)}")]

async def list_tasks_lowlevel():
    try:
        result = str(db.tree)
        return [types.TextContent(type="text", text=result)]
    except Exception as error:
        return [types.TextContent(type="text", text=f"Error: {str(error)}")]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[types.TextContent]:
    if name == "create_task":
        return await create_task_lowlevel(**arguments)
    elif name == "update_task":
        return await update_task_lowlevel(**arguments)
    elif name == "update_status":
        return await update_status_lowlevel(**arguments)
    elif name == "delete_task":
        return await delete_task_lowlevel(**arguments)
    elif name == "get_task":
        return await get_task_lowlevel(**arguments)
    elif name == "list_tasks":
        return await list_tasks_lowlevel()
    elif name == "test_tool":
        return [types.TextContent(type="text", text="Test function is working")]
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_task",
            description="Create a new task",
            inputSchema=CREATE_TASK_SCHEMA,
        ),
        types.Tool(
            name="update_task",
            description="Update task fields (description, DoD, deadline, assignee)",
            inputSchema=UPDATE_TASK_SCHEMA,
        ),
        types.Tool(
            name="update_status",
            description="Change the status of a task (todo, in_progress, done, cancelled) and set a reason",
            inputSchema=UPDATE_STATUS_SCHEMA,
        ),
        types.Tool(
            name="delete_task",
            description="Delete a task by its ID",
            inputSchema=DELETE_TASK_SCHEMA,
        ),
        types.Tool(
            name="get_task",
            description="Get detailed information about a task by its ID",
            inputSchema=GET_TASK_SCHEMA,
        ),
        types.Tool(
            name="list_tasks",
            description="List all tasks in the tree",
            inputSchema=EMPTY_SCHEMA,
        ),
        types.Tool(
            name="test_tool",
            description="Check MCP server health",
            inputSchema=EMPTY_SCHEMA,
        ),
    ]


# async def run_server():
#     from mcp.server.stdio import stdio_server
#
#     async with stdio_server() as streams:
#         await app.run(
#             streams[0], streams[1], app.create_initialization_options()
#         )
#
#
# if __name__ == "__main__":
#     asyncio.run(run_server())

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="example",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())