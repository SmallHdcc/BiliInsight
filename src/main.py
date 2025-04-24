import flet as ft
import threading

from client.bilibili_client import BilibiliClient
from ui.login_screen import setup_login_screen


def main(page: ft.Page):

    # set font
    page.fonts = {
        "pingfang": "./static/PingFang.otf",
    }

    # create theme
    page.theme = ft.Theme(
        font_family="pingfang",
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # set page properties
    page.title = "Bilibili 客户端"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BilibiliClient.THEME_DARK
    page.padding = 0
    page.window_width = 1100
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600

    # Create client instance
    client = BilibiliClient()

    # Set up login screen
    setup_login_screen(page, client)


if __name__ == "__main__":
    ft.app(main)
