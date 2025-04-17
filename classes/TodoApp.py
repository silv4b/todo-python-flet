# classes/TodoApp.py
import asyncio
import flet as ft
from classes.Task import Task
from classes.ConfirmationDialog import ConfirmDialog


class TodoApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.all_tasks = []

        def clear_text(e):
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
            height=400,  # Valor inicial
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

        # Centraliza o app e limita a largura
        self.controls.append(
            ft.Container(
                content=content,
                alignment=ft.alignment.top_center,
                expand=True,
                padding=20,
                width=600,
            )
        )

        # Define o on_resize para ajustar a altura da lista dinamicamente
        self.page.on_resized = self.on_resize
        self.page.run_task(self.initial_resize)

    async def initial_resize(self):
        """Executa o redimensionamento após a página carregar"""
        await asyncio.sleep(0.2)  # Espera a página renderizar
        self.on_resize(None)
        self.update()

    def on_resize(self, e):
        """Calcula o tamanho do listview de acordo com o tamanho da tela"""
        # Obter altura disponível de forma cross-platform
        if self.page.platform == "windows":
            available_height = self.page.window.height - 300
            available_width = self.page.window.width
        else:  # Para navegador
            available_height = self.page.height - 300
            available_width = self.page.width

        print(f"\nPlataforma: {self.page.platform.name}")
        print(
            f"Altura disponível [Total/Calculada]: {available_height + 300}/{available_height}"
        )
        print(f"Largura disponível: {available_width}")

        # Define limites mínimos e máximos
        tasks_view_height = available_height
        print(f"Nova altura do ListView: {tasks_view_height}")

        # Atualiza a altura do ListView
        self.tasks_view.height = tasks_view_height
        self.update()

    def toggle_theme(self, e):
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

    def add_clicked(self, e):
        if self.new_task.value.strip():
            task = Task(
                self.page, self.new_task.value, self.status_changed, self.task_delete
            )
            self.all_tasks.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update_tasks_view()
            self.completed_tasks(self.all_tasks)

    def status_changed(self, task):
        self.update_tasks_view()
        self.clear_completed_tasks_buttom_enable()
        self.completed_tasks(self.all_tasks)

    def task_delete(self, task):
        self.all_tasks.remove(task)
        self.update_tasks_view()
        self.completed_tasks(self.all_tasks)
        self.clear_completed_tasks_buttom_enable()

    def clear_clicked(self, e):

        def confirm_clear():
            tasks_to_remove = [task for task in self.all_tasks if task.completed]
            for task in tasks_to_remove:
                self.all_tasks.remove(task)
            self.update_tasks_view()
            self.completed_tasks(self.all_tasks)
            self.clear_completed_tasks_buttom_enable()
            self.page.open(
                ft.SnackBar(
                    ft.Text("Tarefas removidas com sucesso!"), show_close_icon=True
                )
            )

        confirm_dialog = ConfirmDialog(
            self.page,
            "Confirmar",
            "Tem certeza que deseja limpar todas as tarefas concluídas?",
            confirm_clear,
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

    def tabs_changed(self, e):
        self.on_resize(e)
        self.update_tasks_view()
