"""Comprehensive analysis dashboard for watch history."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

import flet as ft

import logging

logger = logging.getLogger("biliinsight.ui.analysis_view")


def show_analysis_overview(client, history: List[Dict[str, Any]], content_area: ft.Container) -> None:
    """显示数据分析概览页面，包含统计卡片、趋势图和报告。"""
    theme = client.get_current_theme_colors()
    analysis_data = generate_analysis_data(history)

    title = ft.Text("数据分析概览", size=24, weight="bold", color=theme["text"])

    stats_wrap = ft.Wrap(
        controls=[
            create_stat_card(client, "观看总数", f"{analysis_data['total_videos']} 个", ft.Icons.PLAY_CIRCLE_FILL),
            create_stat_card(client, "累计时长", f"{analysis_data['total_hours']} 小时", ft.Icons.TIMER),
            create_stat_card(client, "活跃天数", f"{analysis_data['active_days']} 天", ft.Icons.CALENDAR_MONTH),
            create_stat_card(client, "观看连击", f"{analysis_data['viewing_streak']} 天", ft.Icons.WATER_DROP),
            create_stat_card(client, "常看分区", analysis_data['top_category'], ft.Icons.CATEGORY),
            create_stat_card(client, "常看UP", analysis_data['top_up_name'], ft.Icons.PEOPLE),
        ],
        spacing=15,
        run_spacing=15,
    )

    highlight_section = _create_highlight_section(client, analysis_data)

    daily_progress_chart = create_daily_progress_chart(client, analysis_data)
    category_chart = create_category_chart(client, analysis_data)
    time_chart = create_time_chart(client, analysis_data)

    personality_report = generate_personality_report(analysis_data)
    personality_report_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("分析报告", size=16, weight="bold", color=theme["text"]),
                ft.Container(height=10),
                ft.Markdown(
                    personality_report,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    code_theme="atom-one-dark",
                ),
            ]
        ),
        bgcolor=theme["card"],
        border_radius=10,
        padding=15,
    )

    charts_row = ft.ResponsiveRow(
        controls=[
            ft.Column(
                [
                    ft.Text("分区分布", size=16, weight="bold", color=theme["text"]),
                    ft.Container(height=10),
                    category_chart,
                ],
                col=6,
            ),
            ft.Column(
                [
                    ft.Text("时段分布", size=16, weight="bold", color=theme["text"]),
                    ft.Container(height=10),
                    time_chart,
                ],
                col=6,
            ),
        ],
        spacing=20,
        run_spacing=20,
    )

    content = ft.Column(
        [
            title,
            ft.Container(height=20),
            stats_wrap,
            ft.Container(height=20),
            highlight_section,
            ft.Container(height=20),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("每日观看时长变化", size=16, weight="bold", color=theme["text"]),
                        ft.Container(height=10),
                        daily_progress_chart,
                    ]
                ),
                bgcolor=theme["card"],
                border_radius=10,
                padding=15,
            ),
            ft.Container(height=20),
            ft.Container(
                content=charts_row,
                bgcolor=theme["card"],
                border_radius=10,
                padding=15,
            ),
            ft.Container(height=20),
            personality_report_container,
        ],
        spacing=10,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    content_area.content = content
    content_area.update()


def generate_analysis_data(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """从历史记录中提取统计信息。"""
    logger.debug("开始生成分析数据，历史记录数量: %s", len(history))

    result: Dict[str, Any] = {
        "total_videos": len(history),
        "total_hours": 0,
        "avg_daily": 0,
        "top_category": "暂无数据",
        "categories": {},
        "daily_stats": {},
        "time_distribution": {
            "0-6点": 0,
            "6-12点": 0,
            "12-18点": 0,
            "18-24点": 0,
        },
        "top_up_name": "暂无数据",
        "up_counter": {},
        "active_days": 0,
        "viewing_streak": 0,
    }

    category_counter: Dict[str, int] = {}
    up_counter: Dict[str, int] = {}
    total_progress = 0

    today = datetime.now().date()
    daily_stats: Dict[str, Dict[str, Any]] = {}
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%m-%d")
        daily_stats[date_str] = {"count": 0, "progress": 0, "date": date_str}

    for item in history:
        progress = _get_watch_seconds(item)
        total_progress += progress

        category = (item.get("tag_name") or "").strip()
        if category:
            category_counter[category] = category_counter.get(category, 0) + 1

        author = item.get("author_name") or item.get("author")
        if author:
            up_counter[author] = up_counter.get(author, 0) + 1

        view_at = item.get("view_at")
        if view_at:
            try:
                view_time = datetime.fromtimestamp(int(view_at))
            except (TypeError, ValueError):
                view_time = None
            if view_time:
                hour = view_time.hour
                if 0 <= hour < 6:
                    result["time_distribution"]["0-6点"] += 1
                elif 6 <= hour < 12:
                    result["time_distribution"]["6-12点"] += 1
                elif 12 <= hour < 18:
                    result["time_distribution"]["12-18点"] += 1
                else:
                    result["time_distribution"]["18-24点"] += 1

                date_key = view_time.strftime("%m-%d")
                if date_key in daily_stats:
                    daily_stats[date_key]["count"] += 1
                    daily_stats[date_key]["progress"] += progress

    result["total_hours"] = round(total_progress / 3600, 1)
    result["avg_daily"] = round(len(history) / 7, 1) if history else 0

    if category_counter:
        result["top_category"] = max(category_counter.items(), key=lambda x: x[1])[0]
    result["categories"] = category_counter

    if up_counter:
        result["top_up_name"] = max(up_counter.items(), key=lambda x: x[1])[0]
    result["up_counter"] = up_counter

    result["daily_stats"] = [
        {
            "date": date,
            "count": stats["count"],
            "progress": round(stats["progress"] / 60, 1),
        }
        for date, stats in daily_stats.items()
    ]

    active_days = sum(1 for stats in daily_stats.values() if stats["count"] > 0)
    result["active_days"] = active_days
    result["viewing_streak"] = _calculate_viewing_streak(daily_stats)

    logger.debug("分析数据生成完成: %s", result)
    return result


def create_stat_card(client, title: str, value: str, icon: str) -> ft.Container:
    theme = client.get_current_theme_colors()
    return ft.Container(
        width=190,
        padding=15,
        bgcolor=theme["card"],
        border_radius=12,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, color=client.THEME_PRIMARY, size=24),
                        ft.Text(title, color=theme["text"], size=14),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(value, size=22, weight="bold", color=theme["text"]),
            ],
            spacing=10,
        ),
    )


def create_category_chart(client, data: Dict[str, Any]) -> ft.Column:
    theme = client.get_current_theme_colors()
    chart_content = ft.Column(spacing=8)

    valid_categories = {k: v for k, v in data["categories"].items() if k}
    categories = sorted(valid_categories.items(), key=lambda x: x[1], reverse=True)

    if not categories:
        return ft.Column([
            ft.Text("暂无分区数据", color=theme["text"]),
        ])

    total_value = sum(value for _, value in categories)
    max_bar_width = 400

    for category, value in categories[:8]:
        percent = value / total_value if total_value else 0
        bar_width = int(max_bar_width * percent)
        chart_content.controls.append(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(category, size=13, color=theme["text"]),
                            ft.Row(
                                [
                                    ft.Text(f"{value} 个", size=13, color=theme["text"]),
                                    ft.Text(f"{int(percent * 100)}%", size=13, color=client.THEME_PRIMARY, weight="bold"),
                                ],
                                spacing=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Stack(
                        [
                            ft.Container(
                                bgcolor="#303030",
                                height=8,
                                width=max_bar_width,
                                border_radius=4,
                            ),
                            ft.Container(
                                bgcolor=client.THEME_PRIMARY,
                                height=8,
                                width=bar_width,
                                border_radius=4,
                            ),
                        ]
                    ),
                ],
                spacing=4,
            )
        )

    return chart_content


def create_time_chart(client, data: Dict[str, Any]) -> ft.Row:
    theme = client.get_current_theme_colors()
    chart_bars: List[ft.Control] = []
    time_data = data["time_distribution"]
    max_value = max(time_data.values()) if any(time_data.values()) else 1
    total_value = sum(time_data.values()) or 1

    for time_range, value in time_data.items():
        percent_text = f"{int(value / total_value * 100)}%"
        height_ratio = value / max_value if max_value else 0
        bar_height = max(160 * height_ratio, 4) if value else 4
        chart_bars.append(
            ft.Column(
                [
                    ft.Text(f"{value} 个", size=12, color=theme["text"], text_align=ft.TextAlign.CENTER),
                    ft.Text(percent_text, size=12, color=client.THEME_PRIMARY, weight="bold", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=6),
                    ft.Container(
                        bgcolor=client.THEME_PRIMARY,
                        height=bar_height,
                        width=36,
                        border_radius=ft.border_radius.only(top_left=6, top_right=6),
                        tooltip=f"{time_range}: {value} 个视频 ({percent_text})",
                    ),
                    ft.Text(time_range, size=12, color=theme["text"], text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            )
        )

    return ft.Row(chart_bars, alignment=ft.MainAxisAlignment.SPACE_AROUND)


def create_daily_progress_chart(client, data: Dict[str, Any]) -> ft.Container:
    theme = client.get_current_theme_colors()
    daily_data = data["daily_stats"]
    reference_max = 240
    actual_max = max((item["progress"] for item in daily_data), default=0)
    if actual_max > reference_max:
        reference_max = actual_max * 1.1

    bars = []
    for day_data in daily_data:
        progress = day_data["progress"]
        height_ratio = progress / reference_max if reference_max else 0
        bar_height = max(200 * height_ratio, 4) if progress else 4
        bars.append(
            ft.Column(
                [
                    ft.Text(f"{progress} 分钟", size=12, color=theme["text"], text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        bgcolor=client.THEME_PRIMARY,
                        height=bar_height,
                        width=36,
                        border_radius=ft.border_radius.only(top_left=6, top_right=6),
                        tooltip=f"{day_data['date']}: {day_data['count']} 个视频，{progress} 分钟",
                    ),
                    ft.Text(day_data["date"], size=12, color=theme["text"], text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            )
        )

    return ft.Container(content=ft.Row(bars, spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))


def generate_personality_report(data: Dict[str, Any]) -> str:
    total_videos = data["total_videos"]
    total_hours = data["total_hours"]
    top_category = data["top_category"]
    top_up = data["top_up_name"]
    time_distribution = data["time_distribution"]
    daily_stats = data["daily_stats"]
    viewing_streak = data["viewing_streak"]
    active_days = data["active_days"]

    prime_time = max(time_distribution.items(), key=lambda x: x[1])[0]
    daily_progress = [day["progress"] for day in daily_stats]
    avg_progress = sum(daily_progress) / len(daily_progress) if daily_progress else 0
    variance = sum((p - avg_progress) ** 2 for p in daily_progress) / len(daily_progress) if daily_progress else 0
    viewing_regularity = "规律" if daily_progress and variance < (avg_progress * 0.6 if avg_progress else 1) else "不规律"

    report_lines = ["📊 **B站观看习惯分析**\n"]

    if total_hours > 14:
        report_lines.append(f"过去 7 天你观看了 {total_hours} 小时的内容，是位重度B站用户！")
    elif total_hours > 7:
        report_lines.append(f"过去 7 天你观看了 {total_hours} 小时的内容，属于中度活跃用户。")
    elif total_hours > 0:
        report_lines.append(f"过去 7 天你观看了 {total_hours} 小时的内容，偏向轻度休闲。")
    else:
        report_lines.append("最近几天几乎没有观看记录，或许可以找时间补补番。")

    if total_videos:
        report_lines.append(f"\n你最常关注的分区是「{top_category}」，常看的UP主是「{top_up}」。")
        report_lines.append(f"\n主要观看时间集中在 {prime_time} 时段，最近 7 天里有 {active_days} 天打开过B站。")
    else:
        report_lines.append("\n暂无足够数据生成更详细的偏好分析。")

    report_lines.append(f"\n观看连击为 {viewing_streak} 天，你的观看节奏整体{viewing_regularity}。")

    report_lines.append("\n**个性化建议：**")
    if viewing_regularity == "不规律" and total_hours > 7:
        report_lines.append("- 尝试规划固定的观影时间，避免过度刷视频")
    if prime_time == "0-6点":
        report_lines.append("- 深夜观看较多，注意保证充足睡眠")
    if total_videos and top_category:
        report_lines.append("- 可以多探索不同的分区，丰富观影类型")

    return "\n".join(report_lines)


def _calculate_viewing_streak(daily_stats: Dict[str, Dict[str, Any]]) -> int:
    streak = 0
    max_streak = 0
    for stats in daily_stats.values():
        if stats["count"] > 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak


def _create_highlight_section(client, data: Dict[str, Any]) -> ft.Container:
    theme = client.get_current_theme_colors()
    up_counter = data.get("up_counter", {})

    highlight_controls: List[ft.Control] = []
    avg_daily = data.get("avg_daily", 0)
    total_hours = data.get("total_hours", 0)
    summary_text = None
    if avg_daily or total_hours:
        summary_text = f"平均每日观看 {avg_daily:.1f} 个视频，共 {total_hours:.1f} 小时"
    if summary_text:
        highlight_controls.append(ft.Text(summary_text, size=14, color=theme["text"]))
    if up_counter:
        top_items = sorted(up_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        highlight_controls.append(
            ft.Column(
                [
                    ft.Text("常看UP主", size=16, weight="bold", color=theme["text"]),
                    ft.Wrap(
                        [
                            ft.Chip(
                                label=ft.Text(f"{name} · {count} 次", color=theme["text"]),
                                bgcolor=ft.Colors.with_opacity(0.15, client.THEME_PRIMARY),
                                avatar=ft.Icon(ft.Icons.PERSON, size=16, color=client.THEME_PRIMARY),
                            )
                            for name, count in top_items
                        ],
                        spacing=10,
                        run_spacing=10,
                    ),
                ],
                spacing=8,
            )
        )

    if data.get("categories"):
        top_categories = sorted(data["categories"].items(), key=lambda x: x[1], reverse=True)[:5]
        highlight_controls.append(
            ft.Column(
                [
                    ft.Text("热门分区", size=16, weight="bold", color=theme["text"]),
                    ft.Wrap(
                        [
                            ft.Chip(
                                label=ft.Text(f"{name} · {count} 次", color=theme["text"]),
                                bgcolor=ft.Colors.with_opacity(0.15, client.THEME_PRIMARY),
                                avatar=ft.Icon(ft.Icons.LOCAL_OFFER, size=16, color=client.THEME_PRIMARY),
                            )
                            for name, count in top_categories
                        ],
                        spacing=10,
                        run_spacing=10,
                    ),
                ],
                spacing=8,
            )
        )

    if not highlight_controls:
        highlight_controls.append(ft.Text("暂无足够数据生成亮点分析", color=theme["text"]))

    return ft.Container(
        content=ft.Column(highlight_controls, spacing=15),
        bgcolor=theme["card"],
        border_radius=10,
        padding=15,
    )


def _get_watch_seconds(item: Dict[str, Any]) -> int:
    progress = int(item.get("progress", 0) or 0)
    if progress < 0:
        progress = int(item.get("duration", 0) or 0)
    return max(progress, 0)
