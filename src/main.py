import flet as ft
import threading
import logging

from client.bilibili_client import BilibiliClient
from ui.login_screen import setup_login_screen
from utils.logging_config import setup_logging

# init logging
logger = setup_logging()
logger.info("应用启动")


def main(page: ft.Page):
    logger.info("初始化应用界面")

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

    logger.debug("界面属性设置完成")

    # Create client instance
    client = BilibiliClient()
    logger.debug("客户端实例已创建")

    # Set up login screen
    setup_login_screen(page, client)
    logger.info("登录界面准备完成")


if __name__ == "__main__":
    try:
        logger.info("启动Flet应用")
        ft.app(main)
    except Exception as e:
        logger.exception(f"应用发生未处理异常: {e}")
