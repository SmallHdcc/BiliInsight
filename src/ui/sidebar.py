import flet as ft
from typing import Dict, List, Any

from ui.history_view import show_watch_history
from ui.wordcloud_view import show_wordcloud
from ui.settings_view import show_settings
from ui.analysis_view import show_analysis_overview


def create_sidebar(client, user_info: Dict[str, Any], content_area: ft.Container,
                   history: List[Dict[str, Any]]) -> ft.Container:
    """Create sidebar with user profile and navigation."""
    theme = client.get_current_theme_colors()
    selected_key = "history"
    nav_items: List[ft.Container] = []

    def update_active_nav(active_key: str) -> None:
        nonlocal selected_key
        selected_key = active_key

        for nav_item in nav_items:
            is_active = nav_item.data["key"] == selected_key
            nav_item.data["active"] = is_active
            nav_item.bgcolor = ft.Colors.with_opacity(
                0.2, client.THEME_PRIMARY) if is_active else None
            nav_item.border = ft.border.all(
                1,
                ft.Colors.with_opacity(
                    0.55 if is_active else 0.0, client.THEME_PRIMARY),
            )
            nav_item.update()

    user_profile = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.CircleAvatar(
                        foreground_image_src=user_info["face"],
                        radius=40,
                    ),
                    margin=ft.margin.only(bottom=10),
                ),
                ft.Text(
                    user_info["uname"],
                    size=18,
                    weight="bold",
                    color=theme["text"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    f"UID: {user_info['mid']}",
                    size=14,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        padding=ft.padding.only(top=32, bottom=28),
        alignment=ft.Alignment.CENTER,
    )

    nav_history = create_nav_item(
        client,
        "历史记录",
        ft.Icons.HISTORY,
        "history",
        lambda _: [show_watch_history(
            client, history, content_area), update_active_nav("history")],
        is_active=True,
    )

    nav_analysis = create_nav_item(
        client,
        "数据分析",
        ft.Icons.INSERT_CHART,
        "analysis",
        lambda _: [show_analysis_overview(
            client, history, content_area), update_active_nav("analysis")],
    )

    nav_wordcloud = create_nav_item(
        client,
        "标签词云",
        ft.Icons.CLOUD,
        "wordcloud",
        lambda _: [show_wordcloud(
            client, history, content_area), update_active_nav("wordcloud")],
    )

    nav_settings = create_nav_item(
        client,
        "设置",
        ft.Icons.SETTINGS,
        "settings",
        lambda _: [show_settings(client, content_area),
                   update_active_nav("settings")],
    )

    nav_items = [nav_history, nav_analysis, nav_wordcloud, nav_settings]

    return ft.Container(
        width=220,
        bgcolor=theme["bg"],
        padding=ft.padding.only(left=12, right=12, top=6, bottom=12),
        content=ft.Column(
            [
                user_profile,
                ft.Divider(height=1, color=ft.Colors.with_opacity(
                    0.2, client.THEME_PRIMARY)),
                ft.Container(
                    content=ft.Column(nav_items, spacing=2),
                    margin=ft.margin.only(top=10),
                ),
            ]
        ),
    )


def create_nav_item(client, text: str, icon: str, key: str, on_click, is_active: bool = False) -> ft.Container:
    """Create a navigation item for the sidebar."""
    theme = client.get_current_theme_colors()

    return ft.Container(
        data={"key": key, "active": is_active},
        content=ft.Row(
            [
                ft.Icon(icon, color=theme["text"], size=20),
                ft.Text(text, color=theme["text"], size=16),
            ],
            spacing=15,
        ),
        padding=15,
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(
            0.2, client.THEME_PRIMARY) if is_active else None,
        border=ft.border.all(
            1,
            ft.Colors.with_opacity(
                0.55, client.THEME_PRIMARY) if is_active else ft.Colors.TRANSPARENT,
        ),
        on_hover=lambda e: on_nav_hover(e, client),
        on_click=on_click,
        ink=True,
    )


def on_nav_hover(e, client) -> None:
    """Handle hover effect on navigation items."""
    is_active = bool(e.control.data.get("active"))
    if is_active and e.data != "false":
        return

    if e.data == "true":
        e.control.bgcolor = ft.Colors.with_opacity(0.12, client.THEME_PRIMARY)
    else:
        e.control.bgcolor = ft.Colors.with_opacity(
            0.2, client.THEME_PRIMARY) if is_active else None

    e.control.update()
