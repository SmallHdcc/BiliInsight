"""Watch history view with advanced filtering and insights."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List

import flet as ft

from utils.history_exporter import export_history_to_csv


def show_watch_history(client, history: List[Dict[str, Any]], content_area: ft.Container) -> None:
    """Render the watch history view with filtering, summary and export tools."""
    # 缓存最新历史数据以便其他视图复用
    client.history = history

    theme = client.get_current_theme_colors()
    page = content_area.page

    # 标题区和操作按钮
    title = ft.Text("观看历史", size=24, weight="bold", color=theme["text"])

    filtered_records: List[Dict[str, Any]] = []

    # 摘要信息容器
    summary_wrap = ft.Wrap(spacing=12, run_spacing=12)

    # 历史记录展示容器
    history_grid = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=340,
        child_aspect_ratio=0.68,
        spacing=20,
        run_spacing=20,
        padding=20,
    )
    history_container = ft.Container(expand=True, content=history_grid)

    # 过滤器控件
    search_field = ft.TextField(
        hint_text="搜索标题或UP主...",
        prefix_icon=ft.Icons.SEARCH,
        dense=True,
        border_radius=10,
        autofocus=False,
        on_change=lambda _: update_history_grid(),
        width=260,
    )

    timeframe_filter = ft.Dropdown(
        label="时间范围",
        dense=True,
        border_radius=10,
        options=[
            ft.dropdown.Option("全部时间"),
            ft.dropdown.Option("最近24小时"),
            ft.dropdown.Option("最近3天"),
            ft.dropdown.Option("最近7天"),
            ft.dropdown.Option("最近30天"),
        ],
        value="最近7天",
        on_change=lambda _: update_history_grid(),
        width=150,
    )

    sort_filter = ft.Dropdown(
        label="排序",
        dense=True,
        border_radius=10,
        options=[
            ft.dropdown.Option("最新观看"),
            ft.dropdown.Option("观看时长（高→低）"),
            ft.dropdown.Option("观看时长（低→高）"),
        ],
        value="最新观看",
        on_change=lambda _: update_history_grid(),
        width=170,
    )

    def update_summary(records: Iterable[Dict[str, Any]]) -> None:
        """Rebuild summary chips using the filtered records."""
        record_list = list(records)
        total_seconds = sum(_get_watch_seconds(item) for item in record_list)
        total_minutes = int(total_seconds // 60)

        top_category = _most_common(record_list, key=lambda x: x.get("tag_name") or "") or "暂无数据"
        top_creator = _most_common(record_list, key=lambda x: x.get("author_name") or x.get("author") or "") or "暂无数据"

        summary_wrap.controls = [
            _create_summary_chip(client, ft.Icons.VIDEO_COLLECTION, "视频数量", f"{len(record_list)} 条"),
            _create_summary_chip(client, ft.Icons.ACCESS_TIME, "累计观看", _format_minutes(total_minutes)),
            _create_summary_chip(client, ft.Icons.GROUP, "常看的UP", top_creator),
            _create_summary_chip(client, ft.Icons.CATEGORY, "热门分区", top_category),
        ]
        summary_wrap.update()

    def update_history_grid() -> None:
        """Apply filters, refresh the grid and update summary chips."""
        query = (search_field.value or "").strip().lower()
        timeframe = timeframe_filter.value or "全部时间"
        sort_mode = sort_filter.value or "最新观看"

        filtered = []
        for item in history:
            if query:
                title_text = (item.get("title") or "").lower()
                author_text = (item.get("author_name") or item.get("author") or "").lower()
                if query not in title_text and query not in author_text:
                    continue

            if timeframe != "全部时间" and not _within_timeframe(item, timeframe):
                continue

            filtered.append(item)

        # 排序
        if sort_mode == "最新观看":
            filtered.sort(key=lambda x: x.get("view_at", 0), reverse=True)
        elif sort_mode == "观看时长（高→低）":
            filtered.sort(key=_get_watch_seconds, reverse=True)
        else:
            filtered.sort(key=_get_watch_seconds)

        filtered_records.clear()
        filtered_records.extend(filtered)

        history_grid.controls.clear()
        if not filtered:
            history_container.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF, size=64, color=client.THEME_PRIMARY),
                        ft.Text("没有符合条件的观看记录", size=18, color=theme["text"]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        else:
            for item in filtered:
                history_grid.controls.append(
                    create_history_card(client, item, page)
                )
            history_container.content = history_grid

        history_container.update()
        update_summary(filtered)

    def handle_export(_: ft.ControlEvent) -> None:
        """Export filtered history to CSV and show feedback."""
        export_source = filtered_records or history
        if not export_source:
            _show_snackbar(page, "没有可导出的数据", ft.Colors.AMBER_400)
            return

        try:
            file_path = export_history_to_csv(export_source)
            _show_snackbar(page, f"已导出到 {file_path}", client.THEME_PRIMARY)
        except Exception as exc:  # pragma: no cover - UI feedback
            _show_snackbar(page, f"导出失败: {exc}", ft.Colors.RED_400)

    export_button = ft.ElevatedButton(
        text="导出CSV",
        icon=ft.Icons.DOWNLOAD,
        bgcolor=client.THEME_PRIMARY,
        color=client.THEME_TEXT_DARK,
        on_click=handle_export,
    )

    filter_bar = ft.ResponsiveRow(
        controls=[
            ft.Column([search_field], col=4, col_md=4, col_lg=4),
            ft.Column([timeframe_filter], col=3, col_md=3, col_lg=3),
            ft.Column([sort_filter], col=3, col_md=3, col_lg=3),
            ft.Column([export_button], col=2, col_md=2, col_lg=2),
        ],
        run_spacing=10,
        spacing=10,
    )

    content = ft.Column(
        [
            ft.Row([title], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            filter_bar,
            ft.Container(height=10),
            summary_wrap,
            ft.Container(height=10),
            history_container,
        ],
        spacing=10,
        expand=True,
        key="history_view",
    )

    content_area.content = content
    content_area.update()
    update_history_grid()


def create_history_card(client, item: Dict[str, Any], page: ft.Page) -> ft.Card:
    """Create a modern card for a history item including actions and progress."""
    theme = client.get_current_theme_colors()

    cover_url = item.get("cover", "")
    title = item.get("title", "无标题")
    author = item.get("author_name") or item.get("author") or "未知作者"
    view_time = _format_timestamp(item.get("view_at"))
    progress_seconds = _get_watch_seconds(item)
    duration_seconds = max(int(item.get("duration", 0) or 0), progress_seconds)
    progress_ratio = min(progress_seconds / duration_seconds, 1) if duration_seconds else 0
    progress_text = _format_duration(progress_seconds)
    duration_text = _format_duration(duration_seconds)

    video_url = _resolve_video_url(item)

    action_buttons: List[ft.Control] = []
    if video_url:
        action_buttons.append(
            ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                tooltip="在浏览器中打开",
                icon_color=client.THEME_PRIMARY,
                on_click=lambda _: page.launch_url(video_url),
            )
        )
        action_buttons.append(
            ft.IconButton(
                icon=ft.Icons.CONTENT_COPY,
                tooltip="复制链接",
                icon_color=theme["text"],
                on_click=lambda _: page.set_clipboard(video_url),
            )
        )

    info_controls: List[ft.Control] = [
        ft.Text(
            title if len(title) <= 40 else f"{title[:37]}...",
            size=16,
            weight="bold",
            color=theme["text"],
        ),
        ft.Row(
            [
                ft.Icon(ft.Icons.PERSON, size=14, color=ft.Colors.GREY_400),
                ft.Text(author, size=13, color=ft.Colors.GREY_400),
            ],
            spacing=6,
        ),
    ]

    tag_label = (item.get("tag_name") or "").strip()
    if tag_label:
        info_controls.append(
            ft.Chip(
                label=ft.Text(tag_label, size=12, color=theme["text"]),
                avatar=ft.Icon(ft.Icons.LOCAL_OFFER, size=16, color=client.THEME_PRIMARY),
                bgcolor=ft.Colors.with_opacity(0.15, client.THEME_PRIMARY),
            )
        )

    info_controls.extend(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.SCHEDULE, size=14, color=ft.Colors.GREY_400),
                    ft.Text(view_time, size=13, color=ft.Colors.GREY_400),
                ],
                spacing=6,
            ),
            ft.Row(
                [
                    ft.Icon(ft.Icons.SPEED, size=14, color=ft.Colors.GREY_400),
                    ft.Text(f"观看 {progress_text} / 总时长 {duration_text}", size=13, color=ft.Colors.GREY_400),
                ],
                spacing=6,
            ),
            ft.LinearProgressIndicator(value=progress_ratio, bgcolor=ft.Colors.with_opacity(0.2, client.THEME_PRIMARY)),
        ]
    )

    info_column = ft.Column(info_controls, spacing=6)

    if action_buttons:
        info_column.controls.append(
            ft.Row(action_buttons, spacing=0, alignment=ft.MainAxisAlignment.END)
        )

    return ft.Card(
        elevation=3,
        surface_tint_color=theme["card"],
        margin=0,
        content=ft.Container(
            width=300,
            bgcolor=theme["card"],
            border_radius=12,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Image(
                            src=cover_url,
                            fit=ft.ImageFit.COVER,
                            width=300,
                            height=160,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.1, client.THEME_PRIMARY),
                    ),
                    ft.Container(
                        content=info_column,
                        padding=15,
                    ),
                ],
                spacing=0,
            ),
        ),
    )


def _within_timeframe(item: Dict[str, Any], timeframe_label: str) -> bool:
    days_mapping = {
        "最近24小时": 1,
        "最近3天": 3,
        "最近7天": 7,
        "最近30天": 30,
    }
    days = days_mapping.get(timeframe_label)
    if not days:
        return True

    try:
        view_at = int(item.get("view_at", 0))
    except (TypeError, ValueError):
        return False

    view_time = datetime.fromtimestamp(view_at)
    return datetime.now() - view_time <= timedelta(days=days)


def _get_watch_seconds(item: Dict[str, Any]) -> int:
    progress = int(item.get("progress", 0) or 0)
    if progress < 0:
        progress = int(item.get("duration", 0) or 0)
    return max(progress, 0)


def _resolve_video_url(item: Dict[str, Any]) -> str | None:
    bvid = item.get("bvid") or item.get("history", {}).get("bvid")
    if bvid:
        return f"https://www.bilibili.com/video/{bvid}"
    uri = item.get("uri") or item.get("short_link")
    return uri


def _format_timestamp(timestamp: Any) -> str:
    if not timestamp:
        return "未知时间"
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return "未知时间"


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0秒"
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours}小时")
    if minutes:
        parts.append(f"{minutes}分钟")
    if sec or not parts:
        parts.append(f"{sec}秒")
    return "".join(parts)


def _format_minutes(minutes: int) -> str:
    if minutes <= 0:
        return "0分钟"
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}小时{mins}分钟" if mins else f"{hours}小时"
    return f"{mins}分钟"


def _most_common(records: Iterable[Dict[str, Any]], key) -> str | None:
    counter: Dict[str, int] = {}
    for item in records:
        value = key(item)
        if not value:
            continue
        counter[value] = counter.get(value, 0) + 1
    if not counter:
        return None
    return max(counter.items(), key=lambda kv: kv[1])[0]


def _create_summary_chip(client, icon: str, label: str, value: str) -> ft.Container:
    theme = client.get_current_theme_colors()
    return ft.Container(
        bgcolor=theme["card"],
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        content=ft.Row(
            [
                ft.Icon(icon, color=client.THEME_PRIMARY, size=20),
                ft.Column(
                    [
                        ft.Text(label, size=12, color=ft.Colors.GREY_500),
                        ft.Text(value, size=16, weight="w600", color=theme["text"]),
                    ],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def _show_snackbar(page: ft.Page, message: str, bgcolor: str | None = None) -> None:
    if page is None:
        return
    snackbar = ft.SnackBar(content=ft.Text(message))
    if bgcolor:
        snackbar.bgcolor = bgcolor
    snackbar.open = True
    page.snack_bar = snackbar
    page.update()
