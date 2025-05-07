from .db import init_db
from .db import add_task
from .db import get_tasks
from .db import delete_task, delete_many_tasks
from .db import update_task_status
from .db import update_task_name
from .db import get_current_theme
from .db import update_current_theme

__all__ = [
    "init_db",
    "add_task",
    "get_tasks",
    "delete_task",
    "delete_many_tasks",
    "update_task_status",
    "update_task_name",
    "get_current_theme",
    "update_current_theme",
]
