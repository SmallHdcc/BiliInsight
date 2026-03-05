import threading
import time
from typing import Dict, List, Optional, Any, Tuple

import flet as ft

from client.api import (
    get_qr_code,
    check_login_status,
    get_user_info,
    get_watch_history
)


class BilibiliClient:
    # UI Color Scheme - Dark
    THEME_DARK = "#18191C"     # Dark background
    THEME_CARD_DARK = "#232527"  # Card background in dark mode
    THEME_TEXT_DARK = "#FFFFFF"  # Text color in dark mode

    # UI Color Scheme - Light
    THEME_LIGHT = "#FFFFFF"    # Light background
    THEME_CARD_LIGHT = "#F5F5F5"  # Card background in light mode
    THEME_TEXT_LIGHT = "#333333"  # Text color in light mode

    # Common colors
    THEME_PRIMARY = "#FB7299"  # Bilibili Pink
    THEME_SECONDARY = "#505050"  # Secondary elements
    LOGIN_POLL_INTERVAL_SECONDS = 2
    LOGIN_POLL_MAX_RETRIES = 180

    def __init__(self):
        self.login_cookies = None
        self.tag_names = []
        self.history: List[Dict[str, Any]] = []
        self.is_dark_theme = True  # 默认为深色主题
        self.login_session_id = 0

    def get_current_theme_colors(self):
        """获取当前主题对应的颜色方案"""
        if self.is_dark_theme:
            return {
                "bg": self.THEME_DARK,
                "card": self.THEME_CARD_DARK,
                "text": self.THEME_TEXT_DARK
            }
        else:
            return {
                "bg": self.THEME_LIGHT,
                "card": self.THEME_CARD_LIGHT,
                "text": self.THEME_TEXT_LIGHT
            }

    def get_qr_code(self) -> Tuple[Optional[str], Optional[str]]:
        """Get Bilibili login QR code and return the QR code key."""
        return get_qr_code()

    def check_login_status(self, qrcode_key: str, qr_file_path: str, page: ft.Page, session_id: Optional[int] = None) -> None:
        """Check QR code login status periodically."""
        retries = 0
        while retries < self.LOGIN_POLL_MAX_RETRIES:
            # A new login screen has been rendered; stop polling the stale QR code.
            if session_id is not None and session_id != self.login_session_id:
                break

            status, cookies = check_login_status(qrcode_key)

            if status == 0:  # Login successful
                self.login_cookies = cookies
                self._handle_successful_login(page)
                break
            elif status == 86038:  # QR code expired
                self._handle_expired_qr_code(page)
                break
            elif status < 0:
                self._show_error_page(page, "网络异常，请稍后重试")
                break

            retries += 1
            time.sleep(self.LOGIN_POLL_INTERVAL_SECONDS)
        else:
            self._show_error_page(page, "登录状态轮询超时，请刷新二维码后重试")

        # 删除图片
        import os
        if os.path.exists(qr_file_path):
            os.remove(qr_file_path)

    def _handle_successful_login(self, page: ft.Page) -> None:
        """Handle successful login by setting up the main UI."""
        from ui.main_layout import create_app_layout
        from ui.history_view import show_watch_history

        # Clear all existing content
        page.clean()

        # Get user info
        user_info = self.get_user_info()
        if not user_info:
            self._show_error_page(page, "获取用户信息失败，请重试")
            return

        # Render main layout first, then load history in background.
        self.history.clear()
        content_area = create_app_layout(self, page, user_info, self.history)
        content_area.content = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.ProgressRing(width=42, height=42, stroke_width=3),
                    ft.Text("正在加载观看历史...", size=15, color=ft.Colors.GREY_400),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
        )
        content_area.update()

        def load_history() -> None:
            history = self.get_watch_history() or []
            self.history.clear()
            self.history.extend(history)
            if content_area.page is None:
                return
            show_watch_history(self, self.history, content_area)

        page.run_thread(load_history)

    def _handle_expired_qr_code(self, page: ft.Page) -> None:
        """Handle expired QR code by regenerating a new one."""
        self._reload_app(page)

    def _show_error_page(self, page: ft.Page, message: str) -> None:
        """Display an error page with the given message."""
        from ui.login_screen import setup_login_screen

        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=64,
                            color=self.THEME_PRIMARY),
                    ft.Text(message, size=18, color=self.THEME_TEXT_DARK, weight="bold",
                            text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton(
                        "重试",
                        on_click=lambda _: self._reload_app(page),
                        style=ft.ButtonStyle(
                            color=self.THEME_TEXT_DARK,
                            bgcolor=self.THEME_PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    )
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                alignment=ft.Alignment.CENTER,
                padding=50,
            )
        )
        page.update()

    def _reload_app(self, page: ft.Page) -> None:
        """Reload the application."""
        from ui.login_screen import setup_login_screen

        page.clean()
        page.bgcolor = self.THEME_DARK  # 确保背景色正确

        setup_login_screen(page, self)

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user information using the login cookies."""
        if not self.login_cookies:
            return None

        return get_user_info(self.login_cookies)

    def get_watch_history(self) -> Optional[List[Dict[str, Any]]]:
        """Get user's watch history."""
        if not self.login_cookies:
            return None

        return get_watch_history(self.login_cookies)
