import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from task_tracker.database import InMemoryDatabase, MongoDatabase
from task_tracker.tasks import TaskStatus

pytestmark = pytest.mark.asyncio

@pytest.fixture(params=["inmemory"])
def db(request):
    if request.param == "inmemory":
        return InMemoryDatabase()
    # Для MongoDatabase раскомментируйте и настройте параметры подключения
    # elif request.param == "mongo":
    #     return MongoDatabase("mongodb://localhost:27017", "task_tracker_test")

async def test_create_and_list_tree(db):
    tree_id = await db.create_tree("Test Tree")
    trees = await db.list_trees()
    assert any(t["id"] == tree_id for t in trees)
    assert any(t["name"] == "Test Tree" for t in trees)

async def test_create_and_get_task(db):
    tree_id = await db.create_tree("Test Tree")
    if isinstance(db, InMemoryDatabase):
        parent_id = db.trees[tree_id].root.id
    else:
        tree = await db._load_tree(tree_id)
        parent_id = tree.root.id
    task_id = await db.create_task(tree_id, parent_id, "Subtask", "DoD")
    task = await db.get_task(tree_id, task_id)
    assert task["description"] == "Subtask"
    assert task["dod"] == "DoD"

async def test_update_task(db):
    tree_id = await db.create_tree("Test Tree")
    if isinstance(db, InMemoryDatabase):
        parent_id = db.trees[tree_id].root.id
    else:
        tree = await db._load_tree(tree_id)
        parent_id = tree.root.id
    task_id = await db.create_task(tree_id, parent_id, "Subtask", "DoD")
    await db.update_task(tree_id, task_id, description="Updated", dod="Updated DoD", status=TaskStatus.DONE)
    task = await db.get_task(tree_id, task_id)
    assert task["description"] == "Updated"
    assert task["dod"] == "Updated DoD"
    assert task["status"] == TaskStatus.DONE.value

async def test_delete_task(db):
    tree_id = await db.create_tree("Test Tree")
    if isinstance(db, InMemoryDatabase):
        parent_id = db.trees[tree_id].root.id
    else:
        tree = await db._load_tree(tree_id)
        parent_id = tree.root.id
    task_id = await db.create_task(tree_id, parent_id, "Subtask", "DoD")
    await db.delete_task(tree_id, task_id)
    with pytest.raises(KeyError):
        await db.get_task(tree_id, task_id)

async def test_error_on_missing_tree(db):
    with pytest.raises(KeyError):
        await db.get_task("not_exist", "any")

async def test_error_on_missing_task(db):
    tree_id = await db.create_tree("Test Tree")
    with pytest.raises(KeyError):
        await db.get_task(tree_id, "not_exist") 