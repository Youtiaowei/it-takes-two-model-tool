from __future__ import annotations
"""主应用程序窗口 — 导航栏 + 多页面 + 状态栏"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from config import config
from scanner import ScanResult
from ui.theme import apply_ttk_styles, AVAILABLE_THEMES
from ui.pages import ScanPage, UnpackPage, ReplacePage, RepackPage, SettingsPage
from ui.widgets import LogPanel, ToolStatusBar


PAGES = [
    ("scan",     "[>] 扫描资源",    ScanPage),
    ("unpack",   "[*] 解包资源",    UnpackPage),
    ("replace",  "[/] 模型替换",    ReplacePage),
    ("repack",   "[*] 封包替换",    RepackPage),
    ("settings", "[=] 设置",       SettingsPage),
]


class Application(tk.Tk):
    """
    主应用程序窗口。
    左侧导航栏 + 右侧内容区 + 底部状态栏。
    """

    def __init__(self):
        super().__init__()

        # 窗口设置
        self.title("It Takes Two — 角色模型替换工具")
        self.geometry("1100x720")
        self.minsize(900, 600)

        # 加载主题
        theme_name = config.get("theme", "dark")
        self.current_theme = AVAILABLE_THEMES.get(theme_name, AVAILABLE_THEMES["dark"])
        self.configure(bg=self.current_theme.bg_primary)
        apply_ttk_styles(self, self.current_theme)

        # 共享数据
        self.scan_result: ScanResult | None = None
        self.unpacked_dir: Path | None = None

        # 构建界面
        self._build_layout()

        # 默认导航到第一页
        self._navigate_to("scan")

        # 关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        """构建整体布局"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ──── 左侧导航栏 ────
        nav_frame = tk.Frame(
            self,
            bg=self.current_theme.bg_secondary,
            width=140,
        )
        nav_frame.grid(row=0, column=0, sticky="ns")
        nav_frame.grid_propagate(False)

        # Logo / 标题
        logo = tk.Label(
            nav_frame,
            text="[T]\n双人成行\n模型工具",
            bg=self.current_theme.bg_secondary,
            fg=self.current_theme.fg_primary,
            font=(self.current_theme.font_family, 12, "bold"),
            justify="center",
            pady=15,
        )
        logo.pack(fill="x")

        # 分隔线
        sep = tk.Frame(nav_frame, bg=self.current_theme.separator, height=1)
        sep.pack(fill="x", padx=10)

        # 导航按钮
        self.nav_buttons = {}
        for page_id, label, _ in PAGES:
            btn = tk.Button(
                nav_frame,
                text=label,
                bg=self.current_theme.bg_secondary,
                fg=self.current_theme.fg_secondary,
                activebackground=self.current_theme.accent,
                activeforeground="white",
                relief="flat",
                bd=0,
                anchor="w",
                padx=15,
                pady=8,
                cursor="hand2",
                font=(self.current_theme.font_family, 10),
                command=lambda pid=page_id: self._navigate_to(pid),
            )
            btn.pack(fill="x")
            self.nav_buttons[page_id] = btn

        # 底部版本
        version_label = tk.Label(
            nav_frame,
            text="v0.1.0",
            bg=self.current_theme.bg_secondary,
            fg=self.current_theme.fg_muted,
            font=("", 8),
        )
        version_label.pack(side="bottom", pady=8)

        # ──── 右侧内容区 ────
        content_frame = ttk.Frame(self)
        content_frame.grid(row=0, column=1, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # 页面容器
        self.page_container = ttk.Frame(content_frame, padding=15)
        self.page_container.grid(row=0, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        # ──── 底部状态栏 ────
        self.status_bar = ToolStatusBar(content_frame)
        self.status_bar.grid(row=1, column=0, sticky="ew")

        # ──── 初始化页面 ────
        self.pages = {}
        for page_id, _, page_class in PAGES:
            page = page_class(self.page_container, self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[page_id] = page

    def _navigate_to(self, page_id: str):
        """切换到指定页面"""
        # 通知当前页退出
        current_page = getattr(self, "_current_page", None)
        if current_page:
            current_page.on_exit()

        # 切换显示
        for pid, page in self.pages.items():
            page.grid_remove() if pid != page_id else page.grid()

        # 通知新页进入
        new_page = self.pages[page_id]
        new_page.on_enter()
        self._current_page = new_page

        # 更新导航高亮
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    bg=self.current_theme.accent,
                    fg="white",
                )
            else:
                btn.configure(
                    bg=self.current_theme.bg_secondary,
                    fg=self.current_theme.fg_secondary,
                )

        # 更新状态栏
        page_names = {pid: label for pid, label, _ in PAGES}
        self.status_bar.set_status(f"当前步骤: {page_names.get(page_id, '')}")

    def _on_close(self):
        """关闭窗口前保存配置"""
        config.save()
        self.destroy()
