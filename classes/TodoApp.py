# classes/TodoApp.py
import asyncio
import flet as ft
from classes.Task import Task
from classes.ConfirmationDialog import ConfirmDialog
from classes.SnackBar import SnackBar
from database.db import (
    add_task,
    get_tasks,
    update_task_status,
    delete_task,
    update_task_name,
    delete_many_tasks,
)


class TodoApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.all_tasks = []

        def clear_text(event: ft.ControlEvent):
            self.new_task.value = ""
            self.new_task.suffix.visible = True
            self.new_task.focus()
            self.update()

        self.new_task = ft.TextField(
            hint_text="Adicione uma tarefa...",
            expand=True,
            on_submit=self.add_clicked,
            prefix_icon=ft.Icons.TASK,
            suffix=ft.IconButton(
                icon=ft.Icons.CLOSE,
                on_click=clear_text,
                icon_size=18,
                icon_color=ft.Colors.GREY_600,
                tooltip="Limpar",
            ),
            text_size=16,
            height=48,
            border_radius=8,
            border_color=ft.Colors.GREY_800,
            focused_border_color=ft.Colors.BLUE_400,
            text_vertical_align=0.5,
            max_length=28,
        )

        self.tasks_view = ft.ListView(
            spacing=10,
            auto_scroll=True,
            height=400,
        )

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text="Todas"),
                ft.Tab(text="Ativas"),
                ft.Tab(text="Concluídas"),
            ],
        )

        self.items_left = ft.Text("Nenhuma tarefa.")

        self.clear_completed_tasks_buttom = ft.TextButton(
            text="Limpar Concluídas",
            on_click=self.clear_clicked,
            disabled=True,
        )

        self.toggle_theme_button = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE,
            on_click=self.toggle_theme,
            tooltip="Alternar tema",
        )

        content = ft.Column(
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Tarefas", size=26, weight="bold"),
                        self.toggle_theme_button,
                    ],
                ),
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.IconButton(icon=ft.Icons.ADD, on_click=self.add_clicked),
                    ],
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            self.filter,
                            ft.Container(
                                content=self.tasks_view,
                                expand=True,
                                border_radius=10,
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    self.items_left,
                                    self.clear_completed_tasks_buttom,
                                ],
                            ),
                        ],
                        spacing=10,
                    ),
                    expand=True,
                ),
            ],
        )

        self.controls.append(
            ft.Container(
                content=content,
                alignment=ft.alignment.top_center,
                expand=True,
                padding=20,
                width=600,
            )
        )

        self.page.on_resized = self.on_resize
        self.page.run_task(self.initial_resize)
        self.page.run_task(self.load_tasks_from_db)

    async def initial_resize(self):
        await asyncio.sleep(0.2)
        self.on_resize(None)
        self.update()

    async def task_edit(self, task: Task, new_name: str):
        if task.task_id:
            await update_task_name(task.task_id, new_name)
        self.update_tasks_view()
        SnackBar(self.page, f"Tarefa atualizada para '{new_name}'!")

    def on_resize(self, event: ft.ControlEvent):
        """Calcula o tamanho do listview de acordo com o tamanho da tela"""
        if self.page.platform == "windows":
            available_height = self.page.window.height - 300
            available_width = self.page.window.width
        else:
            available_height = self.page.height - 300
            available_width = self.page.width

        tasks_view_height = available_height
        self.tasks_view.height = tasks_view_height
        self.update()

    async def load_tasks_from_db(self):
        """Recupera todas as tarefas do banco de dados"""
        db_tasks = await get_tasks()
        for task in db_tasks:
            self.all_tasks.append(
                Task(
                    self.page,
                    task.name,
                    self.status_changed,
                    self.task_delete,
                    self.task_edit,
                    task.completed,
                    task.id,
                )
            )
        self.update_tasks_view()
        self.completed_tasks(self.all_tasks)
        self.clear_completed_tasks_buttom_enable()

    def toggle_theme(self, event: ft.ControlEvent):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.toggle_theme_button.icon = ft.Icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.toggle_theme_button.icon = ft.Icons.LIGHT_MODE
        self.page.update()

    def completed_tasks(self, tasks: list):
        all_tasks = len(tasks)
        completed_tasks = len([task for task in self.all_tasks if task.completed])
        if all_tasks == 0:
            self.items_left.value = f"Nenhuma tarefa adicionada."
        elif all_tasks == completed_tasks:
            self.items_left.value = f"Todas as tarefas concluídas."
        else:
            self.items_left.value = (
                f"{completed_tasks}/{all_tasks} tarefa(s) concluída(s)."
            )
        self.page.update()

    def clear_completed_tasks_buttom_enable(self):
        self.clear_completed_tasks_buttom.disabled = not any(
            task.completed for task in self.all_tasks
        )
        self.update()

    async def add_clicked(self, event: ft.ControlEvent):
        if self.new_task.value.strip():
            db_task = await add_task(self.new_task.value.strip())
            task = Task(
                self.page,
                db_task.name,
                self.status_changed,
                self.task_delete,
                self.task_edit,
                False,
                db_task.id,
            )
            self.all_tasks.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update_tasks_view()
            self.completed_tasks(self.all_tasks)
            SnackBar(self.page, f"Tarefa '{task.task_name}' adicionada com sucesso!")

    async def status_changed(self, task: Task):
        await update_task_status(task.task_id, task.completed)
        self.update_tasks_view()
        self.clear_completed_tasks_buttom_enable()
        self.completed_tasks(self.all_tasks)

    async def task_delete(self, task: Task):
        if task.task_id:
            await delete_task(task.task_id)

        self.all_tasks.remove(task)
        self.update_tasks_view()
        self.completed_tasks(self.all_tasks)
        self.clear_completed_tasks_buttom_enable()
        SnackBar(self.page, f"Tarefa '{task.task_name}' removida com sucesso!")

    async def clear_clicked(self, event: ft.ControlEvent):
        async def confirm_clear():
            tasks_to_remove = [task for task in self.all_tasks if task.completed]
            task_ids = [task.task_id for task in tasks_to_remove if task.task_id]

            if task_ids:
                await delete_many_tasks(task_ids)

            self.all_tasks = [task for task in self.all_tasks if not task.completed]

            self.update_tasks_view()
            self.completed_tasks(self.all_tasks)
            self.clear_completed_tasks_buttom_enable()
            SnackBar(self.page, f"{len(tasks_to_remove)} tarefas concluídas removidas!")

        confirm_dialog = ConfirmDialog(
            self.page,
            "Confirmar",
            "Tem certeza que deseja limpar todas as tarefas concluídas?",
            confirm_clear,
            True,
        )
        confirm_dialog.open()

    def update_tasks_view(self):
        self.tasks_view.controls.clear()

        if self.filter.selected_index == 0:
            filtered_tasks = self.all_tasks
        elif self.filter.selected_index == 1:
            filtered_tasks = [task for task in self.all_tasks if not task.completed]
        else:
            filtered_tasks = [task for task in self.all_tasks if task.completed]

        self.tasks_view.controls.extend(filtered_tasks)
        self.update()

    def tabs_changed(self, event: ft.ControlEvent):
        self.on_resize(event)
        self.update_tasks_view()
