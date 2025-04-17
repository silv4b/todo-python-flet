from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    completed = Column(Boolean, default=False)


DATABASE_URL = "sqlite+aiosqlite:///todo.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_task(name: str):
    async with AsyncSessionLocal() as session:
        new_task = TaskModel(name=name)
        session.add(new_task)
        await session.commit()
        return new_task


async def get_tasks():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            TaskModel.__table__.select().order_by(TaskModel.id)
        )
        return result.fetchall()


async def delete_task(task_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            TaskModel.__table__.delete().where(TaskModel.id == task_id)
        )
        await session.commit()


async def update_task_status(task_id: int, completed: bool):
    async with AsyncSessionLocal() as session:
        await session.execute(
            TaskModel.__table__.update()
            .where(TaskModel.id == task_id)
            .values(completed=completed)
        )
        await session.commit()
