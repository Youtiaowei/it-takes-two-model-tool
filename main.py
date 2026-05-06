#!/usr/bin/env python3
"""
《双人成行》角色模型替换工具 — 主入口

It Takes Two Character Model Swapper
一个面向普通玩家的图形化工具，用于替换游戏中的角色模型。

使用方式：
    python main.py

前置条件：
    - Python 3.11+
    - tkinter (通常内置)
    - 可选: UnrealPak, Blender
"""
import sys
import os
import logging

# ─── 适配 PyInstaller 打包环境 ───
if getattr(sys, 'frozen', False):
    # 打包后的 exe 运行环境
    BASE_DIR = sys._MEIPASS
else:
    # 开发环境
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)  # 确保相对路径正确

# ─── 显式导入所有子模块（确保 PyInstaller 打包时能发现它们） ───
# flake8: noqa
import config
import scanner
import unpacker
import model_replacer
import repacker
import backup_manager

# 这些导入确保 ui/ 和 utils/ 子包被打包
from ui import app as ui_app
from ui import pages as ui_pages
from ui import widgets as ui_widgets
from ui import theme as ui_theme
from utils import path_utils
from utils import unreal_helpers

from ui.app import Application


def setup_logging():
    """配置日志输出"""
    log_dir = os.path.join(os.path.expanduser("~"), ".it-takes-two-tool")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("It Takes Two Model Tool 启动")
    logger.info("=" * 50)

    app = Application()
    app.mainloop()

    logger.info("程序退出")


if __name__ == "__main__":
    main()
