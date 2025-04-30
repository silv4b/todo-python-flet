import aiosqlite
import sqlite3
import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Task:
    id: int
    name: str
    completed: bool
    added_at: str
    completed_at: str
    updated_at: str


@dataclass
class Theme:
    id: int
    current_theme: str


DATABASE_FILE = "todo.db"


# Tasks Operations


async def init_db():
    """Inicializa o banco de dados de forma assíncrona"""
    if os.path.exists(DATABASE_FILE):
        return  # Já existe, não precisa inicializar

    async with aiosqlite.connect(DATABASE_FILE) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                added_at TEXT NOT NULL,
                completed_at TEXT,
                updated_at TEXT
            );
            """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS theme (
                id INTEGER PRIMARY KEY DEFAULT 1,
                current_theme TEXT NOT NULL
            );
            """
        )

        # Inserções separadas para melhor controle
        await conn.execute(
            "INSERT OR IGNORE INTO tasks (name, completed) VALUES ('Bem Vindo! 🚀', 0)"
        )

        await conn.execute(
            "INSERT OR IGNORE INTO theme (id, current_theme) VALUES (1, 'dark')"
        )
        await conn.commit()


async def add_task(name: str, added: str, updated: str) -> Task:
    """Adiciona uma nova tarefa"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO tasks (name, completed, added_at, updated_at) VALUES (?,?,?,?)",
                (name, 0, added, updated),
            )
            await conn.commit()
            return Task(
                id=cursor.lastrowid,
                name=name,
                completed=False,
                added_at=added,
                completed_at="",
                updated_at=updated,
            )


async def get_tasks() -> List[Task]:
    """Retorna todas as tarefas"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT id, name, completed, added_at, completed_at, updated_at FROM tasks ORDER BY id"
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                Task(
                    id=row["id"],
                    name=row["name"],
                    completed=bool(row["completed"]),
                    added_at=row["added_at"],
                    completed_at=row["completed_at"],
                    updated_at=row["updated_at"],
                )
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


async def update_task_status(
    task_id: int, completed: bool, updated_at: str, completed_at: str
):
    """Atualiza o status"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        await conn.execute(
            "UPDATE tasks SET completed = ?, updated_at = ?, completed_at = ? WHERE id = ?",
            (
                completed,
                updated_at,
                completed_at if completed else None,
                task_id,
            ),
        )

        await conn.commit()


async def update_task_name(task_id: int, new_name: str, updated_at: str):
    """Atualiza o nome"""
    async with aiosqlite.connect(DATABASE_FILE) as conn:
        await conn.execute(
            "UPDATE tasks SET name = ?, updated_at = ? WHERE id = ?",
            (new_name, updated_at, task_id),
        )
        await conn.commit()


# Theme Operations (sync)


def get_current_theme(theme_id: int = 1) -> Optional[str]:
    """Obtém o tema atual (versão síncrona)"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT current_theme FROM theme WHERE id = ?", (theme_id,)
        )
        row = cursor.fetchone()
        return row["current_theme"] if row else None


def update_current_theme(theme_id: int, new_theme: str) -> str:
    """Atualiza o tema (versão síncrona)"""
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.execute(
            "UPDATE theme SET current_theme = ? WHERE id = ?", (new_theme, theme_id)
        )
        conn.commit()
        return new_theme
