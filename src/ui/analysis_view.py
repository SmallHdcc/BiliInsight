import flet as ft
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("biliinsight.ui.analysis_view")


def show_analysis_overview(client, history: List[Dict[str, Any]], content_area: ft.Container) -> None:
    """显示数据分析概览页面"""
    # 获取当前主题颜色
    theme = client.get_current_theme_colors()

    # 页面标题
    title = ft.Text("数据分析概览", size=24, weight="bold", color=theme["text"])

    # 生成分析数据
    analysis_data = generate_analysis_data(history)

    # 顶部统计卡片
    stats_row = ft.Row(
        [
            create_stat_card(
                client,
                "观看总数",
                f"{analysis_data['total_videos']}个视频",
                ft.Icons.PLAY_CIRCLE_FILL
            ),
            create_stat_card(
                client,
                "累计时长",
                f"{analysis_data['total_hours']}小时",
                ft.Icons.TIMER
            ),
            create_stat_card(
                client,
                "最常观看分区",
                analysis_data['top_category'],
                ft.Icons.CATEGORY
            ),
            create_stat_card(
                client,
                "平均每日",
                f"{analysis_data['avg_daily']}个视频",
                ft.Icons.INSERT_CHART
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # 创建每日观看时长图表
    daily_progress_chart = create_daily_progress_chart(client, analysis_data)

    # 创建分区分布图表
    category_chart = create_category_chart(client, analysis_data)

    # 创建时间分布图表
    time_chart = create_time_chart(client, analysis_data)

    personality_report = generate_personality_report(analysis_data)
    personality_report_container = ft.Container(
        content=ft.Column([
            ft.Text("分析报告", size=16, weight="bold", color=theme["text"]),
            ft.Container(height=10),
            ft.Markdown(
                personality_report,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme="atom-one-dark",
            ),
        ]),
        bgcolor=theme["card"],
        border_radius=10,
        padding=15,
    )

    # 修改布局添加报告区域
    content = ft.Column(
        [
            title,
            ft.Container(height=20),  # 间隔
            stats_row,
            ft.Container(height=20),  # 间隔
            # 每日观看时长图表
            ft.Container(
                content=ft.Column([
                    ft.Text("每日观看时长变化", size=16, weight="bold",
                            color=theme["text"]),
                    ft.Container(height=10),
                    daily_progress_chart
                ]),
                bgcolor=theme["card"],
                border_radius=10,
                padding=15,
            ),

            ft.Container(height=20),  # 间隔

            # 分类和时间分布
            ft.Row(
                [
                    ft.Container(
                        content=category_chart,
                        expand=1,
                        bgcolor=theme["card"],
                        border_radius=10,
                        padding=15,
                    ),
                    ft.Container(
                        content=time_chart,
                        expand=1,
                        bgcolor=theme["card"],
                        border_radius=10,
                        padding=15,
                    ),
                ],
                spacing=20,
            ),

            ft.Container(height=20),  # 间隔
            # 新增: 个性化分析报告
            personality_report_container,
            ft.Container(height=20),  # 间隔
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # 更新内容区域
    content_area.content = content
    content_area.update()


def generate_analysis_data(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """从历史数据生成分析数据"""
    logger.debug(f"开始生成分析数据，历史记录数量: {len(history)}")

    # 初始化结果字典
    result = {
        "total_videos": len(history),
        "total_hours": 0,
        "avg_daily": 0,
        "top_category": "未知",
        "categories": {},
        "daily_stats": {},
        "time_distribution": {
            "0-6点": 0,
            "6-12点": 0,
            "12-18点": 0,
            "18-24点": 0,
        },
    }

    # 统计分类数据
    category_counter = {}
    tag_counter = {}
    total_progress = 0  # 总观看进度（秒）

    # 准备每日统计数据
    # 获取最近7天的日期列表
    today = datetime.now().date()
    daily_stats = {}

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%m-%d")
        daily_stats[date_str] = {
            "count": 0,
            "progress": 0,  # 使用progress而不是duration
            "date": date_str
        }

    # 处理每条历史记录
    for item in history:
        # 累计进度时长
        progress = item.get("progress", 0)
        if progress < 0:
            progress = item.get("duration", 0)
        total_progress += progress

        # 分类统计
        if "tag_name" in item:
            category = item["tag_name"]
            if category not in category_counter:
                category_counter[category] = 0
            category_counter[category] += 1

        # 标签提取和统计
        if "title" in item:
            # 简单处理：将标题分词当作标签（实际应用中可能需要更复杂的处理）
            title = item["title"]
            # 这里应该有更好的分词方式，这里简化处理
            words = [w for w in title.split() if len(w) > 1]
            for word in words:
                if word not in tag_counter:
                    tag_counter[word] = 0
                tag_counter[word] += 1

        # 时间分布
        if "view_at" in item:
            view_time = datetime.fromtimestamp(item["view_at"])
            hour = view_time.hour

            if 0 <= hour < 6:
                result["time_distribution"]["0-6点"] += 1
            elif 6 <= hour < 12:
                result["time_distribution"]["6-12点"] += 1
            elif 12 <= hour < 18:
                result["time_distribution"]["12-18点"] += 1
            else:
                result["time_distribution"]["18-24点"] += 1

            # 每日统计
            date_str = view_time.strftime("%m-%d")
            if date_str in daily_stats:
                daily_stats[date_str]["count"] += 1
                daily_stats[date_str]["progress"] += progress  # 使用progress累加

    # 处理结果

    # 总时长（小时）
    result["total_hours"] = round(total_progress / 3600, 1)

    # 平均每日视频数
    result["avg_daily"] = round(len(history) / 7, 0)

    # 最常看的分类
    if category_counter:
        result["top_category"] = max(
            category_counter.items(), key=lambda x: x[1])[0]

    # 分类统计
    result["categories"] = category_counter

    # 每日数据整理为列表
    result["daily_stats"] = [
        {
            "date": date,
            "count": stats["count"],
            "progress": round(stats["progress"] / 60, 1)  # 转换为分钟，保留一位小数
        }
        for date, stats in daily_stats.items()
    ]

    logger.debug(
        f"分析数据生成完成: 总视频数={result['total_videos']}, 总时长={result['total_hours']}小时")

    return result


def create_stat_card(client, title: str, value: str, icon: str) -> ft.Container:
    """创建统计数据卡片"""
    theme = client.get_current_theme_colors()

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, color=client.THEME_PRIMARY, size=24),
                        ft.Text(title, color=theme["text"], size=14),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=10),  # 间隔
                ft.Text(
                    value,
                    size=22,
                    weight="bold",
                    color=theme["text"],
                ),
            ],
            spacing=0,
        ),
        width=180,
        height=100,
        padding=15,
        bgcolor=theme["card"],
        border_radius=10,
    )


def create_category_chart(client, data: Dict[str, Any]) -> ft.Column:
    """创建分类分布图表"""
    theme = client.get_current_theme_colors()

    # 图表标题
    chart_title = ft.Text("分区分布", size=16, weight="bold", color=theme["text"])

    # 图表内容 - 这里使用条形图
    chart_content = ft.Column(spacing=8)

    # 过滤掉空分区名，然后按数量降序排序
    valid_categories = {k: v for k,
                        v in data["categories"].items() if k.strip() != ""}
    categories = sorted(valid_categories.items(),
                        key=lambda x: x[1], reverse=True)

    if not categories:
        # 没有有效分类数据时显示提示
        return ft.Column([
            chart_title,
            ft.Container(height=15),
            ft.Text("暂无分区数据", color=theme["text"]),
        ], spacing=0)

    # 获取总值用于计算百分比
    total_value = sum(value for _, value in categories)

    # 固定进度条宽度（像素）
    max_bar_width = 400  # 最大进度条宽度

    # 生成每个分类的条形
    for category, value in categories[:8]:  # 只显示前8个分类，避免过多
        # 计算百分比值和条的宽度
        percent = value / total_value  # 实际百分比，0-1之间
        percent_text = f"{int(percent * 100)}%"

        bar_width = int(max_bar_width * percent)

        # 创建一个条形
        chart_content.controls.append(
            ft.Column([
                ft.Row([
                    ft.Text(f"{category}", size=13, color=theme["text"]),
                    ft.Row([
                        ft.Text(f"{value}个", size=13, color=theme["text"]),
                        ft.Text(f"{percent_text}", size=13,
                                color=client.THEME_PRIMARY, weight="bold"),
                    ], spacing=5),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Stack([
                    # 背景条 - 完整宽度
                    ft.Container(
                        bgcolor="#303030",
                        height=8,
                        width=max_bar_width,
                        border_radius=4,
                    ),
                    # 前景条 - 部分宽度
                    ft.Container(
                        bgcolor=client.THEME_PRIMARY,
                        height=8,
                        width=bar_width,
                        border_radius=4,
                    ),
                ]),
            ], spacing=4)
        )

    return ft.Column([
        chart_title,
        ft.Container(height=15),  # 间隔
        chart_content,
    ], spacing=0)


def create_time_chart(client, data: Dict[str, Any]) -> ft.Column:
    """创建时间分布图表"""
    theme = client.get_current_theme_colors()

    # 图表标题
    chart_title = ft.Text("时段分布", size=16, weight="bold", color=theme["text"])

    # 图表内容
    chart_bars = []

    # 获取最大值用于计算高度
    time_data = data["time_distribution"]
    max_value = max(time_data.values()) if time_data else 1
    total_value = sum(time_data.values()) if time_data else 1

    # 创建柱状图
    for time_range, value in time_data.items():
        # 计算高度百分比 (最大高度设为100)
        height_percent_textage = value / max_value if max_value > 0 else 0
        bar_height = 100 * height_percent_textage
        percent_text = f"{int(value / total_value * 100)}%"

        chart_bars.append(
            ft.Column([
                ft.Text(
                    f"{value}个",
                    size=12,
                    color=theme["text"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    percent_text,
                    size=12,
                    color=client.THEME_PRIMARY,
                    weight="bold",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    height=5,  # 小间隔
                ),
                ft.Container(
                    bgcolor=client.THEME_PRIMARY,
                    height=bar_height,
                    width=30,
                    border_radius=ft.border_radius.only(
                        top_left=5, top_right=5),
                    tooltip=f"{value}个视频 ({percent_text})",
                ),
                ft.Text(time_range, size=12, color=theme["text"]),
            ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            )
        )

    return ft.Column([
        chart_title,
        ft.Container(height=15),  # 间隔
        ft.Container(
            content=ft.Row(
                chart_bars,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            height=180,
        )
    ], spacing=0)


def create_daily_progress_chart(client, data: Dict[str, Any]) -> ft.Container:
    """创建每日观看时长图表 - 使用固定参考值计算比例"""
    theme = client.get_current_theme_colors()

    # 获取每日数据
    daily_data = data["daily_stats"]

    # 创建图表容器
    chart_container = ft.Container(height=250)

    # 使用固定参考值而不是最大值
    reference_max = 240  # 4小时(240分钟)设为满高度

    # 找出实际最大值，用于动态调整参考值
    actual_max = max(item["progress"]
                     for item in daily_data) if daily_data else 1

    # 如果实际最大值超过参考值，调整参考值以确保最高的柱子不会超出容器
    if actual_max > reference_max:
        reference_max = actual_max * 1.1  # 留出10%的余量

    # 创建柱状图
    chart_content = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        spacing=5
    )

    # 为每一天创建柱状图
    for day_data in daily_data:
        date = day_data["date"]
        progress = day_data["progress"]  # 分钟
        count = day_data["count"]

        # 计算柱子高度 - 相对于固定参考值
        height_percentage = progress / reference_max
        # 确保即使时间很短也有最小高度显示
        bar_height = max(180 * height_percentage, 5) if progress > 0 else 0

        # 创建柱状图柱子
        chart_content.controls.append(
            ft.Column([
                ft.Text(
                    f"{progress}分钟",
                    size=12,
                    color=theme["text"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    bgcolor=client.THEME_PRIMARY,
                    height=bar_height,
                    width=30,
                    border_radius=ft.border_radius.only(
                        top_left=5, top_right=5),
                    tooltip=f"{date}: {count}个视频，{progress}分钟",
                ),
                ft.Text(
                    date,
                    size=12,
                    color=theme["text"],
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            )
        )

    chart_container.content = chart_content
    return chart_container


def generate_personality_report(data: Dict[str, Any]) -> str:
    """根据用户数据生成分析报告"""

    # # 获取全局平均数据
    # try:
    #     from utils.data_collector import UserDataCollector
    #     collector = UserDataCollector()

    #     # 首先上传当前用户数据
    #     data_to_upload = collector.collect_viewing_data(data)
    #     collector.upload_data(data_to_upload)

    #     # 然后获取平均数据
    #     avg_metrics = collector.get_average_metrics()
    # except Exception as e:
    #     logger.warning(f"获取平均指标数据失败: {e}")
    #     avg_metrics = None

    # 1. 提取分析所需的关键数据
    total_videos = data["total_videos"]
    total_hours = data["total_hours"]
    top_category = data["top_category"]
    avg_daily = data["avg_daily"]
    categories = data["categories"]
    time_distribution = data["time_distribution"]
    daily_stats = data["daily_stats"]

    # 2. 确定用户观看习惯特点

    # 确定主要观看时段
    prime_time = max(time_distribution.items(), key=lambda x: x[1])[0]

    # 计算分类多样性
    category_diversity = len([c for c, v in categories.items() if v > 1])

    # 判断是否有明显的偏好分类
    has_strong_preference = False
    if categories and top_category:
        top_category_count = categories.get(top_category, 0)
        if top_category_count / total_videos > 0.4:  # 超过40%是同一分类
            has_strong_preference = True

    # 观看规律性 - 分析每日观看波动
    daily_progress = [day["progress"] for day in daily_stats]
    if daily_progress:
        avg_progress = sum(daily_progress) / len(daily_progress)
        variance = sum((p - avg_progress) **
                       2 for p in daily_progress) / len(daily_progress)
        viewing_regularity = "规律" if variance < (avg_progress * 0.5) else "不规律"
    else:
        viewing_regularity = "不规律"

    # 3. 生成个性化报告文本
    report = []

    # 开场白
    report.append(f"📊 **B站观看习惯分析**\n")

    # 基本观看量评价
    if total_hours > 14:
        report.append(f"你在过去7天内观看了{total_hours}小时的内容，是个重度B站用户！")
    elif total_hours > 7:
        report.append(f"你在过去7天内观看了{total_hours}小时的内容，算是个中度B站爱好者。")
    else:
        report.append(f"你在过去7天内观看了{total_hours}小时的内容，属于轻度休闲观看。")

    # 分类偏好分析
    if has_strong_preference:
        report.append(f"\n你对「{top_category}」分区有明显偏好，这类视频占据了你大部分观看时间。")
    elif category_diversity > 3:
        report.append(f"\n你的兴趣非常广泛，跨越了{category_diversity}个不同分区，喜欢探索多元内容。")
    else:
        report.append(f"\n你主要关注「{top_category}」等少数几个分区，有比较集中的兴趣范围。")

    # 时间习惯分析与平均比较
    report.append(f"\n你最喜欢在{prime_time}观看视频，这个时段占据了你的主要观看时间。")

    # 观看规律性分析
    report.append(f"\n从每日数据来看，你的观看习惯比较{viewing_regularity}。")

    # 个性化建议
    report.append("\n**个性化建议：**")
    if viewing_regularity == "不规律" and total_hours > 7:
        report.append("- 尝试设定固定的观看时间，避免长时间沉迷")
    if has_strong_preference:
        report.append(f"- 尝试探索更多分区内容，拓展你的兴趣范围")
    if prime_time == "0-6点":
        report.append("- 注意调整作息，避免深夜观看影响睡眠")

    return "\n".join(report)
