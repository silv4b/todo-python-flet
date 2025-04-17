# classes/ConfirmDialog.py
from typing import Callable
import flet as ft


class ConfirmDialog:
    def __init__(
        self, page: ft.Page, title: str, message: str, on_confirm: Callable[[], None]
    ):
        self.page = page
        self.on_confirm = on_confirm

        def close_dlg(event: ft.ControlEvent = None):
            self.dialog.open = False
            self.page.update()

        def handle_confirm(event: ft.ControlEvent):
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
