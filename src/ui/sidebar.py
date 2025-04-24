import flet as ft
from typing import Dict, List, Any

from ui.history_view import show_watch_history
from ui.wordcloud_view import show_wordcloud
from ui.settings_view import show_settings


def create_sidebar(client, user_info: Dict[str, Any], content_area: ft.Container,
                   history: List[Dict[str, Any]]) -> ft.Container:
    """Create sidebar with user profile and navigation."""
    # 获取当前主题颜色
    theme = client.get_current_theme_colors()

    # User profile section
    user_profile = ft.Container(
        content=ft.Column([
            # User avatar
            ft.Container(
                content=ft.CircleAvatar(
                    foreground_image_src=user_info["face"],
                    radius=40,
                ),
                margin=ft.margin.only(bottom=10)
            ),
            # User name
            ft.Text(
                user_info["uname"],
                size=18,
                weight="bold",
                color=theme["text"],
                text_align=ft.TextAlign.CENTER
            ),
            # User ID
            ft.Text(
                f"UID: {user_info['mid']}",
                size=14,
                color=ft.Colors.GREY_400,
                text_align=ft.TextAlign.CENTER
            ),
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        padding=ft.padding.only(top=30, bottom=30),
        alignment=ft.alignment.center,
    )

    # Navigation items
    nav_history = create_nav_item(
        client,
        "历史记录",
        ft.Icons.HISTORY,
        lambda _: show_watch_history(client, history, content_area)
    )

    nav_wordcloud = create_nav_item(
        client,
        "标签词云",
        ft.Icons.CLOUD,
        lambda _: show_wordcloud(client, history, content_area)
    )

    nav_settings = create_nav_item(
        client,
        "设置",
        ft.Icons.SETTINGS,
        lambda _: show_settings(client, content_area)
    )

    # Create sidebar container
    return ft.Container(
        width=220,
        bgcolor=theme["bg"],
        content=ft.Column([
            user_profile,
            ft.Divider(height=1, color=client.THEME_SECONDARY),
            ft.Container(
                content=ft.Column([
                    nav_history,
                    nav_wordcloud,
                    nav_settings,
                ], spacing=0),
                margin=ft.margin.only(top=10)
            ),
        ]),
    )


def create_nav_item(client, text: str, icon: str, on_click) -> ft.Container:
    """Create a navigation item for the sidebar."""
    # 获取当前主题颜色
    theme = client.get_current_theme_colors()

    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, color=theme["text"], size=20),
            ft.Text(text, color=theme["text"], size=16),
        ], spacing=15),
        padding=15,
        border_radius=8,
        on_hover=lambda e: on_nav_hover(e, client),
        on_click=on_click,
        ink=True,
    )


def on_nav_hover(e, client) -> None:
    """Handle hover effect on navigation items."""
    if e.data == "true":  # hover enter
        e.control.bgcolor = client.THEME_SECONDARY
    else:  # hover exit
        e.control.bgcolor = None
    e.control.update()
