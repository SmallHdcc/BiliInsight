import flet as ft


def show_settings(client, content_area: ft.Container) -> None:
    """Display settings page with working functionality."""
    # 获取当前主题颜色
    theme = client.get_current_theme_colors()

    # Page title - 更美观的标题
    title = ft.Text(
        "设置",
        size=26,  # 稍大一些的字体
        weight="w600",  # 使用数字权重更精确
        color=theme["text"],
        text_align=ft.TextAlign.START,
    )

    # Settings options - 更现代化的设置卡片
    settings_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                # Account section - 改进标题样式
                ft.Text(
                    "账户",
                    size=18,
                    weight="w500",  # 稍轻一些更优雅
                    color=theme["text"],
                ),
                ft.Divider(height=1, color=client.THEME_SECONDARY),
                ft.Container(  # 添加容器提供更好的间距
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.LOGOUT,
                                        color=client.THEME_PRIMARY,
                                        size=22),  # 稍大图标
                        title=ft.Text(
                            "退出登录",
                            color=theme["text"],
                            size=15,  # 稍小的字体更精致
                        ),
                        trailing=ft.Icon(
                            ft.Icons.ARROW_FORWARD_IOS,
                            color=theme["text"],
                            size=15
                        ),
                        on_click=lambda _: logout(client, content_area.page)
                    ),
                    margin=ft.margin.symmetric(vertical=5),  # 添加垂直间距
                ),

                # 移除外观部分

                ft.Container(height=20),  # Spacer

                # About section - 统一样式
                ft.Text(
                    "关于",
                    size=18,
                    weight="w500",
                    color=theme["text"],
                ),
                ft.Divider(height=1, color=client.THEME_SECONDARY),
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.INFO,
                            color=client.THEME_PRIMARY,
                            size=22),
                        title=ft.Text(
                            "应用版本",
                            color=theme["text"],
                            size=15,
                        ),
                        trailing=ft.Text(
                            "1.0.0",
                            color=ft.Colors.GREY_400,
                            size=14,  # 版本号稍小
                        ),
                    ),
                    margin=ft.margin.symmetric(vertical=5),
                ),
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.CODE,
                            color=client.THEME_PRIMARY,
                            size=22),
                        title=ft.Text(
                            "关于项目",
                            color=theme["text"],
                            size=15,
                        ),
                        trailing=ft.Icon(
                            ft.Icons.ARROW_FORWARD_IOS,
                            color=theme["text"],
                            size=15
                        ),
                        on_click=lambda _: show_about_dialog(
                            content_area.page, client)
                    ),
                    margin=ft.margin.symmetric(vertical=5),
                ),
            ],
                spacing=12),  # 增加整体间距
            padding=25,  # 稍大的内边距
            bgcolor=theme["card"],
            border_radius=10,  # 增加圆角半径
        ),
        elevation=2,
    )

    content = ft.Column([
        title,
        settings_card
    ], spacing=20)

    content_area.content = content
    content_area.update()


def logout(client, page: ft.Page) -> None:
    """处理用户退出登录功能，通过重启应用来完全重置状态"""

    def handle_logout(e, confirm=False):
        """处理退出登录确认操作"""
        # 关闭确认对话框
        if page.overlay and len(page.overlay) > 0:
            page.overlay.pop()
            page.update()

        # 只有确认才执行退出
        if not confirm:
            return

        try:
            # 清除登录凭证
            client.login_cookies = None

            # 显示加载状态
            page.clean()

            loading = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=40, height=40),
                    ft.Text("正在退出登录...", size=18)
                ], alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                alignment=ft.alignment.center,
                expand=True
            )
            page.add(loading)
            page.update()

            # 延迟短暂时间
            import time
            time.sleep(0.5)

            # 直接返回登录页面，不重启应用
            from ui.login_screen import setup_login_screen
            page.clean()

            # 重置页面属性
            page.title = "Bilibili 客户端"
            # page.scroll = "auto"
            # page.bgcolor = client.THEME_DARK if client.is_dark_theme else client.THEME_LIGHT
            page.update()

            # 重新设置登录页面
            setup_login_screen(page, client)
            # Start login status checking thread

        except Exception as ex:
            # 显示错误信息
            print(f"退出登录异常: {ex}")
            import traceback
            traceback.print_exc()

            # 显示错误界面
            page.clean()
            page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"退出登录时发生错误: {str(ex)}", color="red", size=16),
                        ft.Text("请尝试手动关闭并重启应用", color=ft.Colors.GREY, size=14),
                        ft.ElevatedButton(
                            "重试",
                            on_click=lambda _: logout(client, page)
                        )
                    ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            )
            page.update()

    # 获取主题颜色
    theme = client.get_current_theme_colors()

    # 创建退出确认对话框
    dialog_content = ft.Container(
        width=350,
        padding=20,
        bgcolor=theme["card"],
        border_radius=10,
        content=ft.Column([
            # 标题
            ft.Text("确认退出登录？", size=18, weight="bold", color=theme["text"]),
            ft.Container(height=10),

            # 内容
            ft.Text("您确定要退出当前账号吗？", color=theme["text"]),
            ft.Text("应用将会重启以完成此操作", size=14, color=ft.Colors.GREY_400),
            ft.Container(height=20),

            # 底部按钮
            ft.Row([
                ft.TextButton(
                    "取消",
                    on_click=lambda e: handle_logout(e, False),
                ),
                ft.ElevatedButton(
                    "确认",
                    on_click=lambda e: handle_logout(e, True),
                    bgcolor=client.THEME_PRIMARY,
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
        ], tight=True, spacing=10),
    )

    # 创建半透明背景
    overlay = ft.Stack([
        # 半透明背景层
        ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        ),
        # 居中显示对话框
        ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
        ),
    ])

    # 添加到页面
    page.overlay.append(overlay)
    page.update()
    print("显示退出登录确认对话框")


def toggle_theme(e, client, page: ft.Page, content_area: ft.Container) -> None:
    """Toggle between light and dark theme for the entire application."""
    is_dark = e.control.value
    client.is_dark_theme = is_dark

    # 设置全局主题
    if is_dark:
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = client.THEME_DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = client.THEME_LIGHT

    # 找到主布局中的侧边栏和内容区
    if page.controls and len(page.controls) > 0:
        main_row = page.controls[0]
        if hasattr(main_row, 'controls') and len(main_row.controls) >= 3:
            # 更新侧边栏
            sidebar = main_row.controls[0]
            update_container_theme(sidebar, client, is_dark)

            # 获取当前视图类型并重新渲染
            current_view = content_area.content
            if current_view:
                # 重新渲染对应视图
                from ui.history_view import show_watch_history
                from ui.wordcloud_view import show_wordcloud
                from ui.settings_view import show_settings

                # 获取历史数据
                history = getattr(client, 'history', [])

                # 根据当前视图类型重新渲染
                if hasattr(current_view, 'key') and current_view.key == "history_view":
                    show_watch_history(client, history, content_area)
                elif hasattr(current_view, 'key') and current_view.key == "wordcloud_view":
                    show_wordcloud(client, history, content_area)
                else:
                    # 默认重新渲染设置页面
                    show_settings(client, content_area)

    page.update()


def update_container_theme(container, client, is_dark):
    """递归更新容器及其子控件的主题颜色"""
    theme = client.get_current_theme_colors()

    # 更新容器背景色，特别处理侧边栏
    if hasattr(container, 'bgcolor'):
        if container.width == 220:  # 这是侧边栏的宽度
            container.bgcolor = theme["bg"]
        elif is_dark and container.bgcolor == client.THEME_CARD_LIGHT:
            container.bgcolor = client.THEME_CARD_DARK
        elif not is_dark and container.bgcolor == client.THEME_CARD_DARK:
            container.bgcolor = client.THEME_CARD_LIGHT

    # 更新文本颜色
    if hasattr(container, 'color'):
        if is_dark and container.color == client.THEME_TEXT_LIGHT:
            container.color = client.THEME_TEXT_DARK
        elif not is_dark and container.color == client.THEME_TEXT_DARK:
            container.color = client.THEME_TEXT_LIGHT

    # 递归更新子控件
    if hasattr(container, 'content') and container.content:
        if hasattr(container.content, 'controls'):
            for control in container.content.controls:
                update_container_theme(control, client, is_dark)
        else:
            update_container_theme(container.content, client, is_dark)

    if hasattr(container, 'controls'):
        for control in container.controls:
            update_container_theme(control, client, is_dark)


def show_about_dialog(page: ft.Page, client) -> None:
    """Show about dialog with project information using overlay."""
    # 获取主题颜色
    theme = client.get_current_theme_colors()

    # 创建对话框内容
    dialog_content = ft.Container(
        width=400,
        padding=20,
        bgcolor=theme["card"],
        border_radius=10,
        content=ft.Column([
            # 标题和关闭按钮
            ft.Row([
                ft.Text("关于项目", size=20, weight="bold", color=theme["text"]),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=theme["text"],
                    on_click=lambda e: close_overlay(e, page),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=1, color=client.THEME_SECONDARY),

            # 内容
            ft.Text("Bilibili 客户端 v1.0.0", weight="bold", color=theme["text"]),
            ft.Text("基于 Python 和 Flet 框架开发的 Bilibili 客户端",
                    color=theme["text"]),
            ft.Text("可用于分析用户历史观看数据、生成标签词云等", color=theme["text"]),
            ft.Container(height=10),
            ft.Text("© 2025 毕业设计作品", color=ft.Colors.GREY_400, size=12),
            ft.Container(height=20),

            # 底部按钮
            ft.Row([
                ft.ElevatedButton(
                    "关闭",
                    on_click=lambda e: close_overlay(e, page),
                    bgcolor=client.THEME_PRIMARY,
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True, spacing=10),
    )

    # 创建半透明背景
    overlay = ft.Stack([
        # 半透明背景层
        ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            on_click=lambda e: close_overlay(e, page),  # 点击背景关闭
        ),
        # 居中显示对话框
        ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
        ),
    ])

    # 添加到页面
    page.overlay.append(overlay)
    page.update()
    print("显示关于项目对话框 (使用overlay)")


def close_overlay(e, page):
    """关闭覆盖层"""
    if page.overlay and len(page.overlay) > 0:
        page.overlay.pop()  # 移除最后添加的覆盖层
        page.update()


def close_dialog(e, dialog):
    """Close the dialog."""
    dialog.open = False
    e.page.update()
