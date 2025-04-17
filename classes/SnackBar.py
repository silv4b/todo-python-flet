import flet as ft


class SnackBar:
    def __init__(
        self,
        page: ft.Page,
        snack_message: str,
        show_close_buttom: bool = True,
        duration: int = 2000,
    ):
        self.page = page
        self.snack_message = snack_message
        self.show_close_buttom = show_close_buttom
        self.duration = duration

        self.page.open(
            ft.SnackBar(
                ft.Text(self.snack_message),
                show_close_icon=self.show_close_buttom,
                duration=self.duration,
            )
        )
