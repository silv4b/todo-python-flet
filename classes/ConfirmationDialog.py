import flet as ft
import asyncio
from typing import Callable


class ConfirmDialog:
    def __init__(
        self,
        page: ft.Page,
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        is_async: bool = False,
    ):
        self.page = page
        self.on_confirm = on_confirm

        def close_dlg(event: ft.ControlEvent = None):
            self.dialog.open = False
            self.page.update()

        def handle_confirm(event: ft.ControlEvent):
            close_dlg()

            if not is_async:
                on_confirm()
            else:
                asyncio.run(on_confirm())

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
