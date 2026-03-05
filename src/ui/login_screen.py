import flet as ft
import threading


def setup_login_screen(page: ft.Page, client) -> None:
    """渲染登录页面并在后台异步获取二维码。"""
    page.clean()

    # 每次重绘登录页都创建一个新的会话标识，旧线程会自动失效。
    client.login_session_id += 1
    session_id = client.login_session_id

    qr_image = ft.Image(
        src="",
        key="qr_code",
        width=220,
        height=220,
        fit="contain",
        visible=False,
    )
    status_text = ft.Text(
        "正在连接哔哩哔哩登录服务...",
        size=13,
        color=ft.Colors.GREY_400,
        text_align=ft.TextAlign.CENTER,
    )
    loading_ring = ft.ProgressRing(width=34, height=34, stroke_width=3)
    refresh_button = ft.OutlinedButton(
        content="刷新二维码",
        icon=ft.Icons.REFRESH,
        disabled=True,
    )

    def set_status(message: str, color: str = ft.Colors.GREY_400) -> None:
        status_text.value = message
        status_text.color = color

    def fetch_qr_async() -> None:
        set_status("正在获取二维码...")
        loading_ring.visible = True
        qr_image.visible = False
        refresh_button.disabled = True
        page.update()

        def worker() -> None:
            qr_data = client.get_qr_code()
            if session_id != client.login_session_id:
                return

            if not qr_data:
                set_status("二维码获取失败，请检查网络后重试", ft.Colors.RED_300)
                loading_ring.visible = False
                refresh_button.disabled = False
                page.update()
                return

            qrcode_key, qrcode_path = qr_data
            qr_image.src = qrcode_path
            qr_image.visible = True
            loading_ring.visible = False
            refresh_button.disabled = False
            set_status("二维码已生成，请在手机端扫码登录", ft.Colors.GREEN_300)
            page.update()

            threading.Thread(
                target=client.check_login_status,
                args=(qrcode_key, qrcode_path, page, session_id),
                daemon=True,
            ).start()

        threading.Thread(target=worker, daemon=True).start()

    refresh_button.on_click = lambda _: fetch_qr_async()

    brand_panel = ft.Container(
        padding=ft.padding.symmetric(horizontal=30, vertical=28),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=12,
                            height=12,
                            border_radius=10,
                            bgcolor=client.THEME_PRIMARY,
                        ),
                        ft.Text("BiliSight", size=30, weight="bold",
                                color=ft.Colors.WHITE),
                    ],
                    spacing=10,
                ),
                ft.Text("你的哔哩哔哩观看洞察", size=18, color=ft.Colors.GREY_300),
                ft.Text(
                    "登录后即可查看观看历史、词云和统计分析。",
                    size=14,
                    color=ft.Colors.GREY_400,
                ),
                ft.Container(height=6),
                ft.Row([ft.Icon(ft.Icons.LOCK, size=16, color=client.THEME_PRIMARY),
                        ft.Text("仅使用官方扫码授权", size=13, color=ft.Colors.GREY_300)], spacing=8),
                ft.Row([ft.Icon(ft.Icons.AUTO_GRAPH, size=16, color=client.THEME_PRIMARY),
                        ft.Text("自动整理近 7 天观看记录", size=13, color=ft.Colors.GREY_300)], spacing=8),
                ft.Row([ft.Icon(ft.Icons.PALETTE, size=16, color=client.THEME_PRIMARY),
                        ft.Text("支持深浅主题切换", size=13, color=ft.Colors.GREY_300)], spacing=8),
            ],
            spacing=14,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    qr_panel = ft.Container(
        padding=ft.padding.symmetric(horizontal=30, vertical=24),
        bgcolor="#1D1F24",
        border_radius=18,
        border=ft.border.all(1, "#31343B"),
        content=ft.Column(
            [
                ft.Text("扫码登录", size=22, weight="bold", color=ft.Colors.WHITE),
                ft.Text("请使用哔哩哔哩手机客户端扫描二维码", size=13,
                        color=ft.Colors.GREY_400),
                ft.Container(
                    width=270,
                    height=270,
                    border_radius=14,
                    bgcolor=ft.Colors.WHITE,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Stack(
                        controls=[
                            ft.Column(
                                [
                                    ft.Icon(ft.Icons.QR_CODE_2, size=58,
                                            color=ft.Colors.GREY_300),
                                    loading_ring,
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=14,
                            ),
                            ft.Container(
                                alignment=ft.Alignment.CENTER, content=qr_image),
                        ],
                    ),
                ),
                status_text,
                refresh_button,
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    root = ft.Container(
        expand=True,
        padding=28,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#111216", "#1A1C21", "#121317"],
        ),
        content=ft.Container(
            expand=True,
            border_radius=24,
            bgcolor="#17191E",
            border=ft.border.all(1, "#2B2E36"),
            padding=24,
            content=ft.ResponsiveRow(
                [
                    ft.Column([brand_panel], col={"sm": 12, "md": 5}),
                    ft.Column([qr_panel], col={"sm": 12, "md": 7}),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                run_spacing=24,
            ),
        ),
    )

    page.add(root)
    page.update()
    fetch_qr_async()
