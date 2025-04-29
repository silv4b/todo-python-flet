import flet as ft
from flet import FloatingActionButtonLocation
import asyncio
from classes.Task import Task
from classes.ConfirmationDialog import ConfirmDialog
from classes.SnackBar import SnackBar
from classes.TextField import TextField
from database.db import (
    add_task,
    get_tasks,
    update_task_status,
    delete_task,
    update_task_name,
    delete_many_tasks,
    update_current_theme,
)


class TodoApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.all_tasks = []

        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.CHECK,
            elevation=90,
            hover_elevation=40,
            mini=False,
            on_click=self.complete_all_tasks,
        )

        self.page.floating_action_button_location = (
            FloatingActionButtonLocation.END_FLOAT
        )

        self.new_task = TextField(
            hint_text="Adicione uma tarefa...",
            expand=True,
            on_submit=self.add_clicked,
            prefix_icon=ft.Icons.TASK,
            text_size=16,
            height=48,
            border_radius=8,
            border_color=ft.Colors.GREY_800,
            focused_border_color=ft.Colors.BLUE_400,
            text_vertical_align=0.5,
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

        self.toggle_theme_button = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE,
            on_click=self.toggle_theme,
            tooltip="Alternar tema",
        )

        self.clear_completed_tasks = ft.PopupMenuItem(
            icon=ft.Icons.REMOVE_DONE,
            text="Limpar Concluídas",
            on_click=self.clear_clicked,
            disabled=not any(task.completed for task in self.all_tasks),
        )

        self.uncheck_completed_tasks = ft.PopupMenuItem(
            icon=ft.Icons.UNARCHIVE,
            text="Desmarcar Concluídas",
            on_click=self.uncheck_clicked,
            disabled=not any(task.completed for task in self.all_tasks),
        )

        content = ft.Column(
            spacing=20,
            controls=[
                # Título e botão de mudar de tema
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Tarefas", size=26, weight="bold"),
                        self.toggle_theme_button,
                    ],
                ),
                # Campo de texto e botão de adicionar tarefa
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.IconButton(icon=ft.Icons.ADD, on_click=self.add_clicked),
                        ft.PopupMenuButton(
                            items=[
                                self.clear_completed_tasks,
                                self.uncheck_completed_tasks,
                            ]
                        ),
                    ],
                ),
                # Área das tarefas
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
                                alignment=ft.MainAxisAlignment.START,
                                controls=[
                                    self.items_left,
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
                width=700,
            )
        )

        self.page.on_resized = self.on_resize
        self.page.run_task(self.initialize_async)

    async def complete_all_tasks(self, event: ft.ControlEvent):
        """Marca todas as tarefas visíveis como concluídas"""

        # Verifica se está nas abas permitidas (Todas ou Ativas)
        if self.filter.selected_index not in [0, 1]:
            SnackBar(self.page, "Ação disponível apenas nas abas Todas ou Ativas.")
            return

        if all(task.completed for task in self.all_tasks):
            SnackBar(self.page, "Todas as tarefas já estão concluídas.")
            return

        # Confirmação antes de executar
        async def confirm_complete():
            tasks_to_complete = []

            if self.filter.selected_index == 0:  # Tab "Todas"
                tasks_to_complete = [
                    task for task in self.all_tasks if not task.completed
                ]
            elif self.filter.selected_index == 1:  # Tab "Ativas"
                tasks_to_complete = [
                    task for task in self.all_tasks if not task.completed
                ]

            for task in tasks_to_complete:
                task.completed = True
                task.display_task.value = True
                task.update_task_appearance()
                if task.task_id:
                    await update_task_status(task.task_id, True)

            self.update_tasks_view()
            self.completed_tasks(self.all_tasks)
            self.clear_completed_tasks_buttom_enable()
            self.page.update()

            SnackBar(
                self.page, f"{len(tasks_to_complete)} tarefas marcadas como concluídas!"
            )

        ConfirmDialog(
            self.page,
            "Confirmar",
            f"Deseja marcar todas as tarefas visíveis como concluídas?",
            confirm_complete,
            True,
        ).open()

    async def initialize_async(self):
        await self.initial_resize()
        await self.load_tasks_from_db()

    async def initial_resize(self):
        await asyncio.sleep(0.5)
        self.on_resize(None)
        self.update()

    async def task_edit(self, task: Task, new_name: str):
        if task.task_id:
            await update_task_name(task.task_id, new_name)
        self.update_tasks_view()
        SnackBar(self.page, f"Tarefa atualizada para '{new_name}'.")

    def on_resize(self, event: ft.ControlEvent):
        """Calcula o tamanho do listview de acordo com o tamanho da tela"""
        base_value = 280
        if self.page.platform == "windows":
            available_height = self.page.window.height - base_value
            # available_width = self.page.window.width
        else:
            available_height = self.page.height - base_value
            # available_width = self.page.width

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
        await self.initial_resize()

    def toggle_theme(self, event: ft.ControlEvent):
        if self.page.theme_mode == "DARK":
            self.page.theme_mode = update_current_theme(1, "LIGHT")
            self.toggle_theme_button.icon = ft.Icons.DARK_MODE
        else:
            self.page.theme_mode = update_current_theme(1, "DARK")
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
        enabled = not any(task.completed for task in self.all_tasks)
        # Habilita/Desabilita o Limpar Concluídas
        (
            self.clear_completed_tasks.disabled,
            self.uncheck_completed_tasks.disabled,
        ) = (enabled, enabled)

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
            self.on_resize(None)

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

    async def uncheck_clicked(self, event: ft.ControlEvent):
        if not any(task.completed for task in self.all_tasks):
            SnackBar(self.page, "Não há tarefas concluídas para desmarcar.")
            return

        async def confirm_uncheck():
            tasks_to_uncheck = [task for task in self.all_tasks if task.completed]

            for task in tasks_to_uncheck:
                task.completed = False
                task.update_task_appearance()
                if task.task_id:
                    await update_task_status(task.task_id, False)

            self.update_tasks_view()
            self.completed_tasks(self.all_tasks)
            self.clear_completed_tasks_buttom_enable()
            self.page.update()

            SnackBar(self.page, f"{len(tasks_to_uncheck)} tarefas desmarcadas!")

        ConfirmDialog(
            self.page,
            "Confirmar",
            "Tem certeza que deseja desmarcar todas as tarefas concluídas?",
            confirm_uncheck,
            True,
        ).open()

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

        ConfirmDialog(
            self.page,
            "Confirmar",
            "Tem certeza que deseja limpar todas as tarefas concluídas?",
            confirm_clear,
            True,
        ).open()

    def update_tasks_view(self):
        self.tasks_view.controls.clear()

        if self.filter.selected_index == 0:
            # todas as tarefas
            filtered_tasks = self.all_tasks
        elif self.filter.selected_index == 1:
            # tarefas não concluídas (compreensão de lista)
            filtered_tasks = [task for task in self.all_tasks if not task.completed]
        else:
            # tarefas concluídas (compreensão de lista)
            filtered_tasks = [task for task in self.all_tasks if task.completed]

        self.tasks_view.controls.extend(filtered_tasks)
        self.update()

    def tabs_changed(self, event: ft.ControlEvent):
        self.on_resize(event)
        self.update_tasks_view()
