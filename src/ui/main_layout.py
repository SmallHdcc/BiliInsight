import flet as ft
from typing import Dict, List, Any

from ui.sidebar import create_sidebar


def create_app_layout(client, page: ft.Page, user_info: Dict[str, Any], history: List[Dict[str, Any]]) -> ft.Container:
    """Create the main application layout with sidebar and content area."""
    theme = client.get_current_theme_colors()

    # 缓存最新历史数据，便于主题切换等场景复用
    client.history = history

    # Create content area container that will be updated
    content_container = ft.Container(
        expand=True,
        padding=24,
        bgcolor=theme["bg"],
        content=None
    )

    # Create sidebar with user info and navigation
    sidebar = create_sidebar(client, user_info, content_container, history)

    # Main layout with sidebar and content
    main_layout = ft.Container(
        expand=True,
        padding=18,
        content=ft.Row([
            sidebar,
            ft.VerticalDivider(
                width=1,
                color=client.THEME_SECONDARY
            ),
            content_container
        ], expand=True),
    )

    page.add(main_layout)
    page.update()
    return content_container
