import os
import flet as ft

from client.bilibili_client import BilibiliClient
from ui.login_screen import setup_login_screen
from utils.logging_config import setup_logging

logger = setup_logging()
logger.info("应用启动")


def set_page_attribute(page: ft.Page):
    """配置Flet页面"""
    # 使用相对路径，但基于脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(current_dir, "static")

    # 检查字体是否存在
    font_path = os.path.join(static_dir, "PingFang.otf")
    if os.path.exists(font_path):
        logger.info(f"使用字体: {font_path}")
        page.fonts = {
            "pingfang": font_path,
        }
        page.theme = ft.Theme(
            font_family="pingfang",
            visual_density=ft.VisualDensity.COMFORTABLE,
        )
    else:
        logger.warning(f"找不到字体: {font_path}，使用系统字体")
        page.theme = ft.Theme(
            font_family="微软雅黑",  # 默认中文字体
            visual_density=ft.VisualDensity.COMFORTABLE,
        )

    # 修改图标设置 - 使用完整的本地文件路径
    icon_path = os.path.join(static_dir, "bilibili.ico")
    if os.path.exists(icon_path):
        logger.info(f"使用图标: {icon_path}")
        # 对于window_icon属性，需要使用绝对路径
        page.window_icon = icon_path  # 注意这里使用window_icon而非window_icon_url
    else:
        logger.warning(f"找不到图标文件: {icon_path}")

    logger.debug("界面属性设置完成")

    # 设置页面属性
    page.title = "Bilibili Insight"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BilibiliClient.THEME_DARK
    page.padding = 0
    page.window_width = 1100
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600


def main(page: ft.Page):

    logger.info("初始化应用界面")
    set_page_attribute(page)

    # 创建客户端实例
    client = BilibiliClient()
    logger.debug("客户端实例已创建")

    setup_login_screen(page, client)


if __name__ == "__main__":
    try:
        logger.info("启动Flet应用")
        ft.app(main)
    except Exception as e:
        logger.exception(f"应用发生未处理异常: {e}")
