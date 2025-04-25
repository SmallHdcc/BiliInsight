import flet as ft
import threading


def setup_login_screen(page: ft.Page, client) -> None:
    """设置登录页面，使用Base64图片而不是文件"""

    # 获取新的二维码密钥和Base64图片
    qrcode_key, qrcode_path = client.get_qr_code()

    if not qrcode_key or not qrcode_path:
        # 处理错误情况
        page.add(
            ft.Container(
                content=ft.Text("获取登录二维码失败，请检查网络连接",
                                color="red", size=16),
                alignment=ft.alignment.center,
                padding=20
            )
        )
        page.update()
        return

    # 创建登录卡片
    login_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                # B站Logo
                ft.Container(
                    content=ft.Row([
                        ft.Text(
                            "Bili",
                            size=32,
                            weight="bold",
                            color=client.THEME_PRIMARY,
                        ),
                        ft.Text(
                            "Client",
                            size=32,
                            weight="bold",
                            color=client.THEME_LIGHT,
                        ),
                    ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    margin=ft.margin.only(bottom=20)
                ),
                # 二维码图片
                ft.Container(
                    content=ft.Image(
                        src=qrcode_path,
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    padding=20,
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                    alignment=ft.alignment.center,
                ),

                # 登录说明
                ft.Container(
                    content=ft.Text(
                        "请使用Bilibili手机客户端扫描二维码登录",
                        size=16,
                        color=client.THEME_LIGHT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    margin=ft.margin.only(top=20),
                ),
            ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            width=400,
            padding=50,
            bgcolor=client.THEME_CARD_DARK,
            border_radius=20,
        ),
        elevation=5,
    )

    # 添加到页面
    page.add(
        ft.Container(
            content=login_card,
            alignment=ft.alignment.center,
            expand=True,
        )
    )
    page.update()

    # 启动登录状态检查线程
    import threading
    check_thread = threading.Thread(
        target=client.check_login_status,
        args=(qrcode_key, qrcode_path, page),
        daemon=True
    )
    check_thread.start()
