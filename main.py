import flet as ft
import asyncio
from database.db import init_db, get_current_theme
from classes.TodoApp import TodoApp


def setup_page(page: ft.Page):
    theme: str = get_current_theme(1)

    page.title = "Minhas Tarefas"
    page.theme_mode = theme
    page.window.height = 800
    page.window.width = 500
    page.padding = 20
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
