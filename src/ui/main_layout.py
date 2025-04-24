import flet as ft
from typing import Dict, List, Any

from ui.sidebar import create_sidebar
from ui.history_view import show_watch_history


def create_app_layout(client, page: ft.Page, user_info: Dict[str, Any], history: List[Dict[str, Any]]) -> None:
    """Create the main application layout with sidebar and content area."""
    # Create content area container that will be updated
    content_container = ft.Container(
        expand=True,
        padding=20,
        content=None
    )

    # Create sidebar with user info and navigation
    sidebar = create_sidebar(client, user_info, content_container, history)

    # Main layout with sidebar and content
    main_layout = ft.Row([
        sidebar,
        ft.VerticalDivider(
            width=1,
            color=client.THEME_SECONDARY
        ),
        content_container
    ], expand=True)

    page.add(main_layout)

    # Show history initially
    show_watch_history(client, history, content_container)
    page.update()
