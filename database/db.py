from sqlalchemy import Column, Integer, String, Boolean, select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class TaskModel(Base):
    """Modelo da tabela 'tasks' usando ORM do SQLAlchemy."""

    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    completed = Column(Boolean, default=False)


# Configuração do banco de dados
DATABASE_URL = "sqlite+aiosqlite:///todo.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    """Inicializa o banco de dados, criando as tabelas se não existirem.
    Abordagem: ORM puro (recomendado para operações de schema)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_task(name: str) -> TaskModel:
    """Adiciona uma nova tarefa.
    Abordagem: ORM puro (mais legível e alinhado com o propósito do ORM)."""
    async with AsyncSessionLocal() as session:
        new_task = TaskModel(name=name)  # Cria um objeto Python
        session.add(new_task)  # ORM gerencia a inserção
        await session.commit()
        return new_task  # Retorna o objeto com ID gerado


async def get_tasks() -> list[TaskModel]:
    """Retorna todas as tarefas ordenadas por ID.
    Abordagem: ORM puro (select com objetos Python)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TaskModel).order_by(TaskModel.id))
        return result.scalars().all()  # Retorna instâncias de TaskModel


async def delete_task(task_id: int):
    """Remove uma tarefa por ID.
    Abordagem: Híbrida (ORM + Core para operação direta no banco).
    Motivo: Evita carregar o objeto em memória se não for necessário."""
    async with AsyncSessionLocal() as session:
        # Método 1: Usando delete() (recomendado)
        task = await session.get(TaskModel, task_id)
        if task:
            await session.delete(task)
            await session.commit()


async def delete_many_tasks(task_ids: list[int]):
    """Remove múltiplas tarefas por IDs de uma só vez."""
    async with AsyncSessionLocal() as session:
        await session.execute(delete(TaskModel).where(TaskModel.id.in_(task_ids)))
        await session.commit()


async def update_task_status(task_id: int, completed: bool):
    """Atualiza o status 'completed' de uma tarefa.
    Abordagem: ORM puro (mais clara para atualizar atributos)."""
    async with AsyncSessionLocal() as session:
        task = await session.get(TaskModel, task_id)  # Busca o objeto
        if task:
            task.completed = completed  # Atualiza o atributo
            await session.commit()


async def update_task_name(task_id: int, new_name: str):
    """Atualiza o nome de uma tarefa no banco de dados"""
    async with AsyncSessionLocal() as session:
        task = await session.get(TaskModel, task_id)
        if task:
            task.name = new_name
            await session.commit()
