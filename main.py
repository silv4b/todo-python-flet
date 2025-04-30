import flet as ft
import asyncio
from database.db import init_db, get_current_theme
from classes.TodoApp import TodoApp


def setup_page(page: ft.Page):
    theme: str = get_current_theme(1)
    full_hd_res_width: int = 1920
    full_hd_res_height: int = 1080

    page.title = "Minhas Tarefas"
    page.theme_mode = theme
    # size numbers
    page.window.width = 600
    page.window.height = 900
    # position numbers
    page.window.left = (full_hd_res_width - page.window.width) / 2
    page.window.top = (full_hd_res_height - page.window.height) / 2
    page.update()


def main(page: ft.Page):
    setup_page(page)

    app = TodoApp(page)

    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    content=app,
                    alignment=ft.alignment.top_center,
                    width=600,
                    expand=True,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    # Inicializa o banco de dados antes de iniciar a interface
    asyncio.run(init_db())
    ft.app(target=main)
