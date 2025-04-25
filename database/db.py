import aiosqlite
from typing import List
from dataclasses import dataclass


@dataclass
class Task:
    id: int
    name: str
    completed: bool


DATABASE_FILE = "todo.db"


async def init_db():
    """Inicializa o banco de dados de forma assíncrona"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            )
            """
        )
        await conn.commit()


async def add_task(name: str) -> Task:
    """Adiciona uma nova tarefa"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO tasks (name) VALUES (?)", (name,))
            await conn.commit()
            return Task(id=cursor.lastrowid, name=name, completed=False)


async def get_tasks() -> List[Task]:
    """Retorna todas as tarefas"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT id, name, completed FROM tasks ORDER BY id"
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                Task(id=row["id"], name=row["name"], completed=bool(row["completed"]))
                for row in rows
            ]


async def delete_task(task_id: int):
    """Remove uma tarefa"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        await conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await conn.commit()


async def delete_many_tasks(task_ids: List[int]):
    """Remove múltiplas tarefas"""
    if not task_ids:
        return

    async with aiosqlite.connect(DATABASE_FILE) as conn:
        placeholders = ",".join("?" * len(task_ids))
        await conn.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", task_ids)
        await conn.commit()


async def update_task_status(task_id: int, completed: bool):
    """Atualiza o status"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        await conn.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id)
        )
        await conn.commit()


async def update_task_name(task_id: int, new_name: str):
    """Atualiza o nome"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        await conn.execute(
            "UPDATE tasks SET name = ? WHERE id = ?", (new_name, task_id)
        )
        await conn.commit()
