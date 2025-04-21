import asyncio
from typing import Callable, Self
import flet as ft
from classes.ConfirmationDialog import ConfirmDialog


class Task(ft.Column):
    def __init__(
        self,
        page: ft.Page,
        task_name: str,
        task_status_change: Callable[[Self], None],
        task_delete: Callable[["Task"], None],
        task_edit: Callable[["Task", str], None],  # Novo callback para edição
        completed: bool = False,
        task_id: int = None,
    ):
        super().__init__()
        self.page = page
        self.completed = completed
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.task_edit = task_edit  # Callback para edição
        self.task_id = task_id  # ID do banco de dados
        self.spacing = 10
        self.visible = True

        # Configuração do checkbox com estilo condicional
        self.display_task = ft.Checkbox(
            value=self.completed,
            label=self.task_name,
            label_style=ft.TextStyle(
                size=16,
                decoration=ft.TextDecoration.LINE_THROUGH if self.completed else None,
                color=ft.Colors.GREY_600 if self.completed else None,
            ),
            on_change=self.status_changed,
        )

        # Área de exibição normal da tarefa
        self.display_view = ft.Row(
            controls=[
                ft.Row(
                    controls=[self.display_task],
                    scroll=True,
                    expand=True,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            ft.Icons.EDIT,
                            tooltip="Editar Tarefa",
                            on_click=self.edit_clicked,
                            icon_color=ft.Colors.GREEN,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            tooltip="Remover Tarefa",
                            on_click=self.delete_clicked,
                            icon_color=ft.Colors.RED,
                        ),
                    ]
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.edit_name = ft.TextField(
            expand=True,
            value=self.task_name,
            on_submit=self.save_clicked,
        )

        self.edit_view = ft.Row(
            visible=False,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE,
                    tooltip="Salvar Edição",
                    on_click=self.save_clicked,
                    icon_color=ft.Colors.GREEN,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, event: ft.ControlEvent):
        """Ativa o modo de edição da tarefa"""
        self.edit_name.value = self.task_name
        self.edit_view.visible = True
        self.display_view.visible = False
        self.edit_name.focus()
        self.update()

    def save_clicked(self, event: ft.ControlEvent):
        """Salva as alterações da tarefa"""
        new_name = self.edit_name.value.strip()
        if new_name and new_name != self.task_name:
            self.task_name = new_name
            self.display_task.label = new_name
            asyncio.run(self.task_edit(self, new_name))

        self.update_task_appearance()
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def delete_clicked(self, event: ft.ControlEvent):
        """Solicita confirmação para excluir a tarefa"""

        def confirm_delete():
            asyncio.run(self.task_delete(self))

        confirm = ConfirmDialog(
            self.page,
            "Confirmar exclusão",
            f'Tem certeza que deseja remover a tarefa "{self.task_name}"?',
            confirm_delete,
        )
        confirm.open()

    def status_changed(self, event: ft.ControlEvent):
        """Atualiza o status de conclusão da tarefa"""
        self.completed = self.display_task.value
        self.update_task_appearance()
        asyncio.run(self.task_status_change(self))

    def update_task_appearance(self):
        """Atualiza a aparência visual com base no estado"""
        self.display_task.label_style = ft.TextStyle(
            size=16,
            decoration=ft.TextDecoration.LINE_THROUGH if self.completed else None,
            color=ft.Colors.GREY_600 if self.completed else None,
        )
        self.display_task.value = self.completed
        self.display_task.update()
