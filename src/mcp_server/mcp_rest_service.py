from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_server.mcp_client import handle_llm_tool_call


@asynccontextmanager
async def lifespan(app: FastAPI):
    project_root = str(Path(__file__).parent.parent.parent.absolute())
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            f"{project_root}/src",
            "run",
            "python",
            "-m",
            "mcp_server.mcp_service_lowlevel"
        ],
        env={"PYTHONPATH": project_root}
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            app.state.mcp_session = mcp_session
            app.state.stdio_manager = None
            try:
                yield
            finally:
                pass

app = FastAPI(lifespan=lifespan)

@app.post("/call_tool")
async def call_tool_endpoint(request: Request):
    llm_json = await request.json()
    mcp_session = request.app.state.mcp_session
    result = await handle_llm_tool_call(llm_json, mcp_session)
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server.mcp_rest_service:app", host="0.0.0.0", port=8000, reload=True)
