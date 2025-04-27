import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from task_tracker.database import InMemoryDatabase
from task_tracker.tasks import TaskStatus
from task_tracker.tree import TaskTree

pytestmark = pytest.mark.asyncio

@pytest.fixture()
def db():
    return InMemoryDatabase()

async def test_create_and_get_task(db):
    parent_id = db.tree.root.id
    task_id = await db.create_task(parent_id, "Subtask", "DoD")
    task = await db.get_task(task_id)
    assert task["description"] == "Subtask"
    assert task["dod"] == "DoD"

async def test_update_task(db):
    parent_id = db.tree.root.id
    task_id = await db.create_task(parent_id, "Subtask", "DoD")
    await db.update_task(task_id, description="Updated", dod="Updated DoD", status=TaskStatus.DONE.value)
    task = await db.get_task(task_id)
    assert task["description"] == "Updated"
    assert task["dod"] == "Updated DoD"
    assert task["status"] == TaskStatus.DONE.value

async def test_delete_task(db):
    parent_id = db.tree.root.id
    task_id = await db.create_task(parent_id, "Subtask", "DoD")
    await db.delete_task(task_id)
    with pytest.raises(KeyError):
        await db.get_task(task_id)

async def test_error_on_missing_task(db):
    with pytest.raises(KeyError):
        await db.get_task("not_exist")

async def test_create_nested_subtasks(db):
    root_id = db.tree.root.id
    sub1_id = await db.create_task(root_id, "Level 1", "DoD1")
    sub2_id = await db.create_task(sub1_id, "Level 2", "DoD2")
    sub3_id = await db.create_task(sub2_id, "Level 3", "DoD3")
    # Проверяем, что Level 3 действительно под Level 2
    sub2 = await db.get_task(sub2_id)
    assert any(st["id"] == sub3_id for st in sub2["subtasks"])
    # Проверяем, что Level 2 под Level 1
    sub1 = await db.get_task(sub1_id)
    assert any(st["id"] == sub2_id for st in sub1["subtasks"])

async def test_update_task_partial_fields(db):
    parent_id = db.tree.root.id
    task_id = await db.create_task(parent_id, "Subtask", "DoD", deadline=None, assignee=None)
    await db.update_task(task_id, assignee="user1")
    task = await db.get_task(task_id)
    assert task["assignee"] == "user1"
    assert task["description"] == "Subtask"
    assert task["dod"] == "DoD"

async def test_delete_subtask_and_check_parent(db):
    parent_id = db.tree.root.id
    sub_id = await db.create_task(parent_id, "Subtask", "DoD")
    await db.delete_task(sub_id)
    parent = await db.get_task(parent_id)
    assert all(st["id"] != sub_id for st in parent["subtasks"])

async def test_cannot_delete_root_task(db):
    root_id = db.tree.root.id
    with pytest.raises(Exception):
        await db.delete_task(root_id)

async def test_tree_serialization_roundtrip(db):
    # Добавим пару задач
    root_id = db.tree.root.id
    t1 = await db.create_task(root_id, "Task1", "DoD1")
    t2 = await db.create_task(root_id, "Task2", "DoD2")
    # Сериализация
    dct = db.tree.to_dict()
    json_str = db.tree.to_json()
    # Десериализация
    tree2 = TaskTree.from_dict(dct)
    assert tree2.root.description == db.tree.root.description
    assert len(tree2.root.subtasks) == 2
    # Проверка JSON
    tree3 = TaskTree.from_json(json_str)
    assert tree3.root.description == db.tree.root.description
    assert len(tree3.root.subtasks) == 2

async def test_find_task_by_id(db):
    root_id = db.tree.root.id
    sub1_id = await db.create_task(root_id, "Level 1", "DoD1")
    sub2_id = await db.create_task(sub1_id, "Level 2", "DoD2")
    # Используем прямой доступ к TaskTree
    found = db.tree.get(sub2_id)
    assert found is not None
    assert found.description == "Level 2"

async def test_create_subtask_with_invalid_parent(db):
    with pytest.raises(KeyError):
        await db.create_task("not_exist", "Should fail", "DoD") 