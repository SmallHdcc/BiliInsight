import logging
import os
import sys
from datetime import datetime


def setup_logging():
    """配置日志系统，将日志存储在项目根目录的Log文件夹中"""
    # 获取项目根目录
    # 假设当前文件位于 src/utils/logging_config.py，需要回退两级找到根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录
    project_root = os.path.dirname(os.path.dirname(current_dir))  # 项目根目录

    # 创建Log文件夹
    log_dir = os.path.join(project_root, "Log")
    os.makedirs(log_dir, exist_ok=True)

    # 创建日志文件名（按日期）
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"biliinsight_{current_date}.log")

    # 获取根日志记录器
    logger = logging.getLogger("biliinsight")
    logger.setLevel(logging.DEBUG)

    # 清除已有的处理器
    if logger.handlers:
        logger.handlers.clear()

    # 配置文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # 配置控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # 控制台只显示INFO级别以上的消息

    # 设置日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"日志系统初始化完成，日志文件：{log_file}")
    return logger
