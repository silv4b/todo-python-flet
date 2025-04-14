# main.py
import flet as ft
from classes.TodoApp import TodoApp


def setup_page(page: ft.Page):
    page.title = "Minhas Tarefas"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.height = 700
    page.window.width = 400
    page.padding = 20
    page.scroll = "none"  # scroll desativado na página toda
    page.update()


def main(page: ft.Page):
    setup_page(page)

    app = TodoApp(page)

    # Adicionando a Row com alinhamento e largura fixada para centralizar o app
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
            alignment=ft.MainAxisAlignment.CENTER,  # Centraliza a Row horizontalmente
        )
    )


ft.app(target=main)
