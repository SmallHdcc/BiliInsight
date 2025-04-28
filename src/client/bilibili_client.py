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
from ui.main_layout import create_app_layout
from ui.history_view import show_watch_history
from ui.wordcloud_view import show_wordcloud
from ui.settings_view import show_settings


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

    def __init__(self):
        self.login_cookies = None
        self.tag_names = []
        self.is_dark_theme = True  # 默认为深色主题

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

    def check_login_status(self, qrcode_key: str, qr_file_path: str, page: ft.Page) -> None:
        """Check QR code login status periodically."""
        while True:
            status, cookies = check_login_status(qrcode_key)

            if status == 0:  # Login successful
                self.login_cookies = cookies
                self._handle_successful_login(page)

                break
            elif status == 86038:  # QR code expired
                self._handle_expired_qr_code(page)
                break

        # 删除图片
        import os
        if os.path.exists(qr_file_path):
            os.remove(qr_file_path)

    def _handle_successful_login(self, page: ft.Page) -> None:
        """Handle successful login by setting up the main UI."""
        # Clear all existing content
        page.clean()

        # Get user info
        user_info = self.get_user_info()
        if not user_info:
            self._show_error_page(page, "获取用户信息失败，请重试")
            return

        # Get watch history
        history = self.get_watch_history()
        if not history:
            history = []

        # Create modern UI layout
        create_app_layout(self, page, user_info, history)

    def _handle_expired_qr_code(self, page: ft.Page) -> None:
        """Handle expired QR code by regenerating a new one."""
        # Clear error messages first
        page.controls = [c for c in page.controls if not (
            hasattr(c, 'key') and c.key == "error_message")]

        # Add expired notice
        page.add(
            ft.Container(
                content=ft.Text("二维码已失效，正在刷新...",
                                size=16,
                                color=self.THEME_TEXT_LIGHT,
                                weight="bold",
                                text_align=ft.TextAlign.CENTER
                                ),
                margin=ft.margin.only(bottom=20),
                key="error_message"
            )
        )
        page.update()

        # Remove notice after 2 seconds
        time.sleep(2)
        page.controls = [c for c in page.controls if not (
            hasattr(c, 'key') and c.key == "error_message")]

        # Regenerate QR code
        new_qrcode_key = self.get_qr_code()
        if new_qrcode_key:
            # Update QR code image
            for control in page.controls:
                if hasattr(control, 'key') and control.key == "qr_code":
                    control.src = "qr_code.png"
                    control.update()
                    break

            page.update()

            # Start new checking thread
            threading.Thread(
                target=self.check_login_status,
                args=(new_qrcode_key, page),
                daemon=True
            ).start()
        else:
            self._show_error_page(page, "生成新的二维码失败，请刷新页面重试")

    def _show_error_page(self, page: ft.Page, message: str) -> None:
        """Display an error page with the given message."""
        from ui.login_screen import setup_login_screen

        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=64,
                            color=self.THEME_PRIMARY),
                    ft.Text(message, size=18, color=self.THEME_TEXT, weight="bold",
                            text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton(
                        "重试",
                        on_click=lambda _: self._reload_app(page),
                        style=ft.ButtonStyle(
                            color=self.THEME_TEXT,
                            bgcolor=self.THEME_PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    )
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                alignment=ft.alignment.center,
                padding=50,
            )
        )
        page.update()

    def _reload_app(self, page: ft.Page) -> None:
        """Reload the application."""
        from ui.login_screen import setup_login_screen

        page.clean()
        page.bgcolor = self.THEME_DARK  # 确保背景色正确

        # Get new QR code
        new_qrcode_key = self.get_qr_code()
        if new_qrcode_key:
            setup_login_screen(page, self)

            # Start login status checking thread
            import threading
            threading.Thread(
                target=self.check_login_status,
                args=(new_qrcode_key, page),
                daemon=True
            ).start()
        else:
            self._show_error_page(page, "无法生成登录二维码，请检查网络连接")

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
