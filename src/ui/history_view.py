import time
import flet as ft
from typing import Dict, List, Any


def show_watch_history(client, history: List[Dict[str, Any]], content_area: ft.Container) -> None:
    """Display watch history in a grid view with modern design."""
    # 获取当前主题颜色
    theme = client.get_current_theme_colors()

    # Page title
    title = ft.Text("观看历史", size=24, weight="bold", color=theme["text"])

    # Create grid for history items
    history_grid = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=320,
        child_aspect_ratio=0.7,
        spacing=20,
        run_spacing=20,
        padding=20,
    )

    if not history:
        content = ft.Column([
            title,
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF,
                            size=64, color=client.THEME_PRIMARY),
                    ft.Text("暂无观看历史", size=18, color=theme["text"]),
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                alignment=ft.alignment.center,
                expand=True,
            )
        ], spacing=20, expand=True, key="history_view")
    else:
        # Add items to grid
        for item in history:
            history_grid.controls.append(
                create_history_card(client, item)
            )

        content = ft.Column([
            title,
            history_grid
        ], spacing=20, expand=True, key="history_view")

    # Update content area
    content_area.content = content
    content_area.update()


def create_history_card(client, item: Dict[str, Any]) -> ft.Card:
    """Create a modern card for a history item."""
    # 获取当前主题颜色
    theme = client.get_current_theme_colors()

    cover_url = item.get("cover", "")
    title = item.get("title", "无标题")
    author = item.get("author_name", "未知作者")
    view_at = item.get("view_at", "")

    # Format timestamp if available
    view_time = ""
    if view_at:
        try:
            import time
            view_time = time.strftime(
                "%Y-%m-%d %H:%M", time.localtime(int(view_at)))
        except:
            view_time = "未知时间"

    return ft.Card(
        elevation=2,
        surface_tint_color=theme["card"],
        content=ft.Container(
            content=ft.Column([
                # Video cover with gradient overlay
                ft.Stack([
                    ft.Container(
                        content=ft.Image(
                            src=cover_url,
                            fit=ft.ImageFit.COVER,
                            width=280,
                            height=160,
                        ),
                        border_radius=ft.border_radius.only(
                            top_left=8, top_right=8
                        ),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    # Play button overlay
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.PLAY_CIRCLE_FILL,
                            color=ft.Colors.WHITE,
                            size=50,
                        ),
                        alignment=ft.alignment.center,
                    ),
                ]),
                # Video details
                ft.Container(
                    content=ft.Column([
                        # Video title (truncate if too long)
                        ft.Text(
                            title if len(
                                title) < 40 else title[:37] + "...",
                            size=16,
                            weight="bold",
                            color=theme["text"],
                        ),
                        # Author
                        ft.Row([
                            ft.Icon(ft.Icons.PERSON, size=14,
                                    color=ft.Colors.GREY_400),
                            ft.Text(author, size=14,
                                    color=ft.Colors.GREY_400),
                        ], spacing=5),
                        # View time
                        ft.Row([
                            ft.Icon(ft.Icons.SCHEDULE, size=14,
                                    color=ft.Colors.GREY_400),
                            ft.Text(view_time, size=14,
                                    color=ft.Colors.GREY_400),
                        ], spacing=5),
                    ], spacing=8),
                    padding=15,
                ),
            ], spacing=0),
            width=280,
            bgcolor=theme["card"],
            border_radius=8,
        ),
        margin=0,
    )
