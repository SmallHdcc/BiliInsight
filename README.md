# BiliInsight

一个基于 **Flet** 的 B 站观看历史分析工具。通过扫码登录 Bilibili 后，你可以快速拉取近 7 天观看记录，并在桌面端查看历史、分析统计、词云与导出内容。

## 功能特性

- 🔐 **Bilibili 扫码登录**：通过网页端二维码授权登录。
- 📜 **观看历史拉取**：自动分页获取近 7 天观看记录（默认最多请求 20 页）。
- 📊 **分析视图**：按分区/标签等维度查看观看情况（由 UI 分析页展示）。
- ☁️ **词云生成**：支持基于历史标题生成词云。
- 📁 **历史导出**：支持将观看历史导出到本地文件。
- 🎨 **深色主题界面**：默认深色风格，桌面端窗口布局优化。

## 技术栈

- Python 3.9+
- [Flet 0.26.0](https://flet.dev)
- requests
- qrcode / Pillow

## 项目结构

```text
src/
├── main.py                  # 入口：应用启动与页面配置
├── client/
│   ├── api.py               # Bilibili API 调用（登录、用户信息、历史）
│   └── bilibili_client.py   # 客户端状态与流程编排
├── ui/                      # 登录、主布局、历史、分析、词云、设置等页面
├── utils/                   # 日志、导出、词云处理工具
└── static/                  # 字体和图标资源
```

## 安装与运行

### 1) 安装依赖

推荐使用 Poetry：

```bash
poetry install
```

如果你使用 pip，请至少安装：

```bash
pip install flet==0.26.0 requests qrcode pillow
```

### 2) 运行应用

```bash
poetry run flet run src/main.py
```

> 也可以直接运行 `poetry run flet run`（依赖 `tool.flet.app.path = "src"` 配置）。

### 3) 打包（可选）

以 macOS 为例：

```bash
poetry run flet build macos -v
```

## 使用说明

1. 启动应用后，使用 Bilibili 客户端扫描二维码。
2. 登录成功后自动进入主界面并拉取观看历史。
3. 在侧边栏切换历史、分析、词云、设置等视图。
4. 在需要时导出历史记录用于留档或二次分析。

## 注意事项

- 本项目依赖 Bilibili 开放接口行为，若接口变更可能导致功能异常。
- 历史拉取默认范围为最近 7 天，如需调整可修改 `get_watch_history()` 的 `days` 参数。
- 二维码图片会在登录流程结束后自动删除。

## 开发建议

- 入口文件：`src/main.py`
- API 逻辑：`src/client/api.py`
- 页面逻辑：`src/ui/*.py`
- 建议提交前先运行：

```bash
poetry run python -m py_compile src/main.py
```

## License

当前仓库未显式提供 License 文件。如需开源分发，请先补充许可证声明。
