import logging

from mcp.server.fastmcp import FastMCP
from task_tracker.database import TaskDatabase
from task_tracker.tasks import Task
from task_tracker.schemas import TaskStatus

MCP_SERVER_NAME = "task-tracker-mcp"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

# Инициализируем MCP сервер
mcp = FastMCP(MCP_SERVER_NAME)

# Инициализируем базу данных
db = TaskDatabase()

@mcp.tool()
async def create_tree(name: str) -> str:
    """Создает новое дерево задач.
    
    Args:
        name: Название дерева задач
    """
    tree_id = await db.create_tree(name)
    return f"Дерево задач '{name}' создано с ID: {tree_id}"

@mcp.tool()
async def delete_tree(tree_id: str) -> str:
    """Удаляет дерево задач и все его задачи.
    
    Args:
        tree_id: ID дерева задач
    """
    await db.delete_tree(tree_id)
    return f"Дерево задач {tree_id} удалено"

@mcp.tool()
async def list_trees() -> str:
    """Возвращает список всех деревьев задач."""
    trees = await db.list_trees()
    if not trees:
        return "Нет доступных деревьев задач"
    
    result = "Доступные деревья задач:\n"
    for tree in trees:
        result += f"- {tree['name']} (ID: {tree['id']})\n"
    return result

@mcp.tool()
async def create_task(tree_id: str, description: str, dod: str, deadline: str | None = None, assignee: str | None = None) -> str:
    """Создает новую задачу в указанном дереве.
    
    Args:
        tree_id: ID дерева задач
        description: Описание задачи
        dod: Критерии приемки
        deadline: Дедлайн (опционально)
        assignee: Исполнитель (опционально)
    """
    task = Task(
        description=description,
        dod=dod,
        deadline=deadline,
        assignee=assignee
    )
    await db.create_task(task, tree_id)
    return f"Задача создана с ID: {task.id}"

@mcp.tool()
async def update_task(tree_id: str, task_id: str, description: str | None = None, dod: str | None = None) -> str:
    """Обновляет существующую задачу в указанном дереве.
    
    Args:
        tree_id: ID дерева задач
        task_id: ID задачи
        description: Новое описание (опционально)
        dod: Новые критерии приемки (опционально)
    """
    task = await db.get_task(task_id, tree_id)
    if not task:
        return f"Задача с ID {task_id} не найдена в дереве {tree_id}"
    
    task.update(
        description=description,
        dod=dod
    )
    await db.update_task(task, tree_id)
    return f"Задача {task_id} обновлена"

@mcp.tool()
async def close_task(tree_id: str, task_id: str, status: str, reason: str | None = None) -> str:
    """Закрывает задачу в указанном дереве.
    
    Args:
        tree_id: ID дерева задач
        task_id: ID задачи
        status: Статус (done/cancelled)
        reason: Причина закрытия (опционально)
    """
    task = await db.get_task(task_id, tree_id)
    if not task:
        return f"Задача с ID {task_id} не найдена в дереве {tree_id}"
    
    task.close(TaskStatus(status), reason)
    await db.update_task(task, tree_id)
    return f"Задача {task_id} закрыта"

@mcp.tool()
async def delete_task(tree_id: str, task_id: str) -> str:
    """Удаляет задачу из указанного дерева.
    
    Args:
        tree_id: ID дерева задач
        task_id: ID задачи
    """
    await db.delete_task(task_id, tree_id)
    return f"Задача {task_id} удалена"

@mcp.tool()
async def get_task(tree_id: str, task_id: str) -> str:
    """Получает информацию о задаче из указанного дерева.
    
    Args:
        tree_id: ID дерева задач
        task_id: ID задачи
    """
    task = await db.get_task(task_id, tree_id)
    if not task:
        return f"Задача с ID {task_id} не найдена в дереве {tree_id}"
    return str(task)

@mcp.tool()
async def test_tool() -> str:
    """Тестовая функция для проверки работы MCP сервера."""
    return "Тестовая функция работает"

if __name__ == "__main__":
    mcp.run(transport='stdio')