import os
import shutil
import PyInstaller.__main__

# 应用名称
APP_NAME = "BiliInsight"

# 清理旧的构建文件
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# 静态文件路径
static_path = "src/static"

# 检查静态文件夹是否存在
if not os.path.exists(static_path):
    print(f"警告: 静态文件夹 '{static_path}' 不存在!")
else:
    print(f"找到静态文件夹: '{static_path}'")

# 准备 PyInstaller 参数
pyinstaller_args = [
    "src/main.py",                   # 主程序入口
    f"--name={APP_NAME}",            # 应用名称
    "--onedir",                      # 创建单文件夹应用
    "--noconsole",                   # 不显示控制台窗口
    "--clean",                       # 清理临时文件
    f"--add-data={static_path};static",  # 添加静态文件

    # 减小体积的选项
    "--noupx",                       # 不使用UPX (更稳定)
    "--strip",                       # 去除符号表

    # 排除不必要的模块
    "--exclude-module=tkinter",      # 如果不使用tkinter
    "--exclude-module=unittest",     # 测试模块
    "--exclude-module=pydoc",        # 文档
    "--exclude-module=xml",          # 如果不用XML
]

# 如果有图标文件，添加图标
icon_path = os.path.join(static_path, "bilibili.ico")
if os.path.exists(icon_path):
    pyinstaller_args.append(f"--icon={icon_path}")
else:
    print(f"警告: 图标文件 '{icon_path}' 不存在!")

# 运行 PyInstaller
PyInstaller.__main__.run(pyinstaller_args)

print(f"打包完成！应用位于 dist/{APP_NAME} 文件夹中")
