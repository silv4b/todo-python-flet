# classes/ConfirmDialog.py
import flet as ft


class ConfirmDialog:
    def __init__(self, page: ft.Page, title: str, message: str, on_confirm):
        self.page = page
        self.on_confirm = on_confirm

        def close_dlg(e=None):
            self.dialog.open = False
            self.page.update()

        def handle_confirm(e):
            close_dlg()
            on_confirm()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Não", on_click=close_dlg),
                ft.TextButton("Sim", on_click=handle_confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def open(self):
        self.page.add(self.dialog)
        self.dialog.open = True
        self.page.update()
