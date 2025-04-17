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
    ):
        super().__init__()
        self.page = page
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.spacing = 10
        self.visible = True

        self.display_task = ft.Checkbox(
            value=False,
            label=self.task_name,
            label_style=ft.TextStyle(size=16),
            on_change=self.status_changed,
        )

        # Envolve o Checkbox em uma Row com largura fixa e rolagem
        task_label_row = ft.Row(
            controls=[self.display_task],
            scroll=True,
            expand=True,
        )

        self.edit_name = ft.TextField(expand=True, on_submit=self.save_clicked)

        self.display_view = ft.Row(
            controls=[
                task_label_row,  # Substitui o Checkbox direto pela Row com rolagem
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

        self.edit_view = ft.Row(
            visible=False,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE,
                    tooltip="Atualizar Tarefa",
                    on_click=self.save_clicked,
                    icon_color=ft.Colors.GREEN,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.controls = [self.display_view, self.edit_view]

    def save_clicked(self, event: ft.ControlEvent):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def edit_clicked(self, event: ft.ControlEvent):
        self.edit_name.value = self.display_task.label
        self.edit_view.visible = True
        self.display_view.visible = False
        self.edit_name.focus()
        self.update()

    def delete_clicked(self, event: ft.ControlEvent):
        def confirm_delete():
            self.task_delete(self)

        confirm = ConfirmDialog(
            self.page,
            "Confirmar exclusão",
            f'Tem certeza que deseja remover a tarefa "{self.task_name}"?',
            confirm_delete,
        )
        confirm.open()

    def status_changed(self, event: ft.ControlEvent):
        self.completed = self.display_task.value
        self.task_status_change(self)
