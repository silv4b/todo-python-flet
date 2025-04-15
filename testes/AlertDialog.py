import flet as ft


def main(page: ft.Page):
    page.title = "AlertDialog examples"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def handle_yes(e):
        page.close(dlg_modal)
        page.add(ft.Text("Ação confirmada!", color="green"))

    def handle_no(e):
        page.close(dlg_modal)
        page.add(ft.Text("Ação cancelada!", color="red"))

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to delete all those files?"),
        actions=[
            ft.TextButton("Yes", on_click=handle_yes),
            ft.TextButton("No", on_click=handle_no),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: page.add(
            ft.Text("Modal dialog dismissed"),
        ),
    )

    page.add(
        ft.ElevatedButton("Open modal dialog", on_click=lambda e: page.open(dlg_modal)),
    )


ft.app(main)
