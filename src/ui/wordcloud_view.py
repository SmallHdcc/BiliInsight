import base64
from io import BytesIO
import flet as ft
from typing import Dict, List, Any

from utils.wordcloud_gen import generate_wordcloud


def show_wordcloud(client, history: List[Dict[str, Any]], content_area: ft.Container) -> None:
    """Generate and display a word cloud from watch history tags."""
    # 获取当前主题颜色
    theme = client.get_current_theme_colors()

    # Page title
    title = ft.Text("标签词云", size=24, weight="bold", color=theme["text"])

    # Extract tags from history
    tags = []
    for item in history:
        if "tag_name" in item and item["tag_name"]:
            tags.append(item["tag_name"])

    if not tags:
        content = ft.Column([
            title,
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CLOUD_OFF, size=64,
                            color=client.THEME_PRIMARY),
                    ft.Text("没有可用的标签数据", size=18, color=theme["text"]),
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                alignment=ft.alignment.center,
                expand=True,
            )
        ], spacing=20, expand=True, key="wordcloud_view")
    else:
        try:
            # 使用当前主题背景色生成词云
            bg_color = theme["bg"]

            # Generate word cloud and get base64 image
            from utils.wordcloud_gen import generate_wordcloud
            img_base64 = generate_wordcloud(tags, bg_color)

            # Display word cloud
            wordcloud_image = ft.Image(
                src_base64=img_base64,
                fit=ft.ImageFit.CONTAIN,
            )

            content = ft.Column([
                title,
                ft.Container(
                    content=wordcloud_image,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=20),
                    border_radius=15,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    expand=True,
                )
            ], spacing=10, expand=True, key="wordcloud_view")
        except Exception as e:
            content = ft.Column([
                title,
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=64,
                                color=client.THEME_PRIMARY),
                        ft.Text(f"生成词云图时出错: {str(e)}",
                                size=18, color=theme["text"]),
                    ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            ], spacing=20, expand=True, key="wordcloud_view")

    # Update content area
    content_area.content = content
    content_area.update()
