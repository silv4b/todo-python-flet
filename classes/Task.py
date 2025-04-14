import flet as ft


class Task(ft.Column):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.spacing = 10
        self.visible = True

        self.display_task = ft.Checkbox(
            value=False,
            label=self.task_name,
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

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.edit_view.visible = True
        self.display_view.visible = False
        self.edit_name.focus()
        self.update()

    def delete_clicked(self, e):
        self.task_delete(self)

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)
