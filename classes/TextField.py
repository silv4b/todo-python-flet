import flet as ft
from typing import Callable, Optional


class TextField(ft.TextField):
    """TextField Personalizado"""

    def __init__(
        self,
        hint_text: str,
        expand: bool,
        on_submit: Callable[[], None],
        prefix_icon: ft.Icons,
        text_size: int,
        height: int,
        border_radius: int,
        border_color: ft.Colors,
        focused_border_color: ft.colors,
        text_vertical_align: float | int,
        suffix: Optional[ft.Control] = None,
    ):
        super().__init__()
        self.hint_text = hint_text
        self.expand = expand
        self.on_submit = on_submit
        self.prefix_icon = prefix_icon
        self.text_size = text_size
        self.height = height
        self.border_radius = border_radius
        self.border_color = border_color
        self.focused_border_color = focused_border_color
        self.text_vertical_align = text_vertical_align

        if suffix is None:
            self.suffix = ft.IconButton(
                icon=ft.Icons.CLOSE,
                on_click=self._clear_text,
                icon_size=18,
                icon_color=ft.Colors.GREY_600,
                tooltip="Limpar",
            )
        else:
            self.suffix = suffix

    def _clear_text(self, event: ft.ControlEvent):
        """Método interno para limpar o texto do campo."""
        self.value = ""
        self.update()
