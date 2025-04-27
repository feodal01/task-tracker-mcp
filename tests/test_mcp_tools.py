import os
import sys
import pytest
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mcp_server import mcp_service

pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
def reset_db(monkeypatch):
    # Сбросить базу перед каждым тестом
    mcp_service.db = mcp_service.InMemoryDatabase()
    yield

async def test_create_task():
    result = await mcp_service.create_task(
        description="Test task",
        dod="DoD for test",
        deadline=None,
        assignee=None,
        parent_id=None
    )
    assert "Task created with ID:" in result

async def test_get_task():
    # Сначала создаём задачу
    create_result = await mcp_service.create_task(
        description="Test get",
        dod="DoD get",
        deadline=None,
        assignee=None,
        parent_id=None
    )
    task_id = create_result.split(": ")[-1]
    get_result = await mcp_service.get_task(task_id)
    assert "Test get" in get_result
    assert "DoD get" in get_result

async def test_update_task():
    create_result = await mcp_service.create_task(
        description="To update",
        dod="DoD update",
        deadline=None,
        assignee=None,
        parent_id=None
    )
    task_id = create_result.split(": ")[-1]
    update_result = await mcp_service.update_task(
        task_id=task_id,
        description="Updated desc",
        dod="Updated DoD",
        status="done",
        close_reason=None,
        deadline=None,
        assignee="user1"
    )
    assert f"Task {task_id} updated" in update_result
    get_result = await mcp_service.get_task(task_id)
    assert "Updated desc" in get_result
    assert "Updated DoD" in get_result
    assert "user1" in get_result

async def test_close_task():
    create_result = await mcp_service.create_task(
        description="To close",
        dod="DoD close",
        deadline=None,
        assignee=None,
        parent_id=None
    )
    task_id = create_result.split(": ")[-1]
    close_result = await mcp_service.close_task(
        task_id=task_id,
        status="done",
        reason="Completed"
    )
    assert f"Task {task_id} closed" in close_result
    get_result = await mcp_service.get_task(task_id)
    assert "done" in get_result or "DONE" in get_result
    assert "Completed" in get_result

async def test_delete_task():
    create_result = await mcp_service.create_task(
        description="To delete",
        dod="DoD delete",
        deadline=None,
        assignee=None,
        parent_id=None
    )
    task_id = create_result.split(": ")[-1]
    delete_result = await mcp_service.delete_task(task_id)
    assert f"Task {task_id} deleted" in delete_result
    with pytest.raises(KeyError):
        await mcp_service.get_task(task_id)

async def test_list_tasks():
    await mcp_service.create_task(
        description="Task 1",
        dod="DoD 1",
        deadline=None,
        assignee=None,
        parent_id=None
    )
    await mcp_service.create_task(
        description="Task 2",
        dod="DoD 2",
        deadline=None,
        assignee=None,
        parent_id=None
    )
    tasks_str = await mcp_service.list_tasks()
    assert "Task 1" in tasks_str
    assert "Task 2" in tasks_str

async def test_tool_health():
    result = await mcp_service.test_tool()
    assert result == "Test function is working" 