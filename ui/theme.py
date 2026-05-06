"""
主题与样式常量 — 暗色/亮色主题，专业游戏工具风格
"""
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass


@dataclass
class Theme:
    """一组主题颜色常量"""
    name: str

    # 主色
    bg_primary: str          # 主背景
    bg_secondary: str        # 次要背景 / 卡片
    bg_tertiary: str         # 输入框、列表背景
    fg_primary: str          # 主文字
    fg_secondary: str        # 次要文字
    fg_muted: str            # 弱化文字

    # 强调色
    accent: str              # 主强调色
    accent_hover: str        # 强调色悬停
    success: str             # 成功
    warning: str             # 警告
    error: str               # 错误
    info: str                # 信息

    # 组件
    button_bg: str           # 按钮背景
    button_fg: str           # 按钮文字
    button_accent_bg: str    # 强调按钮
    entry_bg: str            # 输入框背景
    progress_bg: str         # 进度条背景
    progress_fg: str         # 进度条填充
    separator: str           # 分隔线

    # 字体
    font_family: str = "Microsoft YaHei UI"  # 中文字体优先
    font_size_small: int = 10
    font_size_normal: int = 11
    font_size_large: int = 14
    font_size_title: int = 18


# ──── 暗色主题 (默认) ────
DARK = Theme(
    name="dark",
    bg_primary="#1a1a2e",
    bg_secondary="#16213e",
    bg_tertiary="#0f3460",
    fg_primary="#e8e8e8",
    fg_secondary="#a0a0b0",
    fg_muted="#6c6c80",
    accent="#e94560",
    accent_hover="#ff6b81",
    success="#2ecc71",
    warning="#f39c12",
    error="#e74c3c",
    info="#3498db",
    button_bg="#2a2a4a",
    button_fg="#e8e8e8",
    button_accent_bg="#c0392b",
    entry_bg="#1e2a4a",
    progress_bg="#2a2a4a",
    progress_fg="#e94560",
    separator="#2a2a4a",
)

# ──── 亮色主题 ────
LIGHT = Theme(
    name="light",
    bg_primary="#f5f6fa",
    bg_secondary="#ffffff",
    bg_tertiary="#dcdde1",
    fg_primary="#2f3640",
    fg_secondary="#636e72",
    fg_muted="#b2bec3",
    accent="#e84118",
    accent_hover="#c23616",
    success="#27ae60",
    warning="#f39c12",
    error="#e74c3c",
    info="#3498db",
    button_bg="#dcdde1",
    button_fg="#2f3640",
    button_accent_bg="#e84118",
    entry_bg="#ffffff",
    progress_bg="#dcdde1",
    progress_fg="#e84118",
    separator="#dcdde1",
)


AVAILABLE_THEMES = {
    "dark": DARK,
    "light": LIGHT,
}


# ──── ttk Style 配置 ────

def apply_ttk_styles(root: tk.Tk, theme: Theme):
    """将主题应用到 ttk 组件"""
    style = ttk.Style(root)
    style.theme_use("clam")

    # 通用
    style.configure(".", background=theme.bg_primary, foreground=theme.fg_primary,
                    font=(theme.font_family, theme.font_size_normal))

    # Frame
    style.configure("TFrame", background=theme.bg_primary)
    style.configure("Card.TFrame", background=theme.bg_secondary)
    style.configure("Header.TFrame", background=theme.bg_secondary)

    # Label
    style.configure("TLabel", background=theme.bg_primary, foreground=theme.fg_primary)
    style.configure("Card.TLabel", background=theme.bg_secondary, foreground=theme.fg_primary)
    style.configure("Title.TLabel", font=(theme.font_family, theme.font_size_title, "bold"),
                    foreground=theme.fg_primary)
    style.configure("Heading.TLabel", font=(theme.font_family, theme.font_size_large, "bold"),
                    foreground=theme.fg_primary)
    style.configure("Muted.TLabel", foreground=theme.fg_muted)
    style.configure("Success.TLabel", foreground=theme.success)
    style.configure("Error.TLabel", foreground=theme.error)
    style.configure("Warning.TLabel", foreground=theme.warning)
    style.configure("Accent.TLabel", foreground=theme.accent)

    # Button
    style.configure("TButton", background=theme.button_bg, foreground=theme.button_fg,
                    font=(theme.font_family, theme.font_size_normal),
                    borderwidth=1, relief="flat", padding=(12, 6))
    style.map("TButton",
              background=[("active", theme.accent_hover)],
              foreground=[("active", "#ffffff")])

    # 强调按钮
    style.configure("Accent.TButton", background=theme.accent, foreground="#ffffff",
                    font=(theme.font_family, theme.font_size_normal, "bold"),
                    borderwidth=0, padding=(16, 8))
    style.map("Accent.TButton",
              background=[("active", theme.accent_hover), ("disabled", "#555")])

    # Entry
    style.configure("TEntry", fieldbackground=theme.entry_bg, foreground=theme.fg_primary,
                    insertcolor=theme.fg_primary, borderwidth=1, relief="solid",
                    padding=(8, 4))

    # Progressbar
    style.configure("TProgressbar", background=theme.progress_fg,
                    troughcolor=theme.progress_bg, borderwidth=0, thickness=8)

    # Treeview
    style.configure("Treeview", background=theme.bg_secondary, foreground=theme.fg_primary,
                    fieldbackground=theme.bg_secondary, borderwidth=0)
    style.map("Treeview", background=[("selected", theme.accent)])
    style.configure("Treeview.Heading", background=theme.bg_tertiary,
                    foreground=theme.fg_primary, font=(theme.font_family, theme.font_size_small, "bold"))

    # Scrollbar
    style.configure("TScrollbar", background=theme.bg_tertiary, troughcolor=theme.bg_primary,
                    bordercolor=theme.bg_primary, arrowcolor=theme.fg_primary)

    # Notebook
    style.configure("TNotebook", background=theme.bg_primary, borderwidth=0)
    style.configure("TNotebook.Tab", background=theme.bg_tertiary, foreground=theme.fg_primary,
                    padding=(12, 6), font=(theme.font_family, theme.font_size_normal))
    style.map("TNotebook.Tab", background=[("selected", theme.accent)])

    # Separator
    style.configure("TSeparator", background=theme.separator)

    # Labelframe
    style.configure("TLabelframe", background=theme.bg_primary, foreground=theme.fg_primary)
    style.configure("TLabelframe.Label", background=theme.bg_primary, foreground=theme.fg_primary)
