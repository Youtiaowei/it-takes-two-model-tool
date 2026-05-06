from __future__ import annotations
"""自定义 GUI 组件 — 拖拽区、文件列表、日志面板等"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Callable


class DropZone(ttk.Frame):
    """
    拖拽文件放置区。
    用户可以将 FBX 文件拖拽到此区域，或点击浏览。
    """

    def __init__(
        self,
        parent,
        text: str = "拖拽 FBX 文件到此处",
        accept_extensions: tuple = (".fbx", ".FBX"),
        on_file_selected: Callable[[Path], None] | None = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.accept_extensions = accept_extensions
        self.on_file_selected = on_file_selected
        self._current_path: Path | None = None

        # 配置样式
        self.configure(relief="groove", borderwidth=2, padding=20)
        self._setup_ui(text)

    def _setup_ui(self, text: str):
        self.grid_columnconfigure(0, weight=1)

        # 图标占位 (使用 Unicode 符号)
        self.icon_label = ttk.Label(
            self,
            text="[F]",
            font=("", 32),
            style="Muted.TLabel",
        )
        self.icon_label.grid(row=0, column=0, pady=(0, 5))

        # 提示文字
        self.hint_label = ttk.Label(
            self,
            text=text,
            style="Muted.TLabel",
            wraplength=280,
        )
        self.hint_label.grid(row=1, column=0, pady=(0, 10))

        # 文件路径显示
        self.path_var = tk.StringVar(value="")
        self.path_label = ttk.Label(
            self,
            textvariable=self.path_var,
            style="Muted.TLabel",
            font=("Consolas", 9),
            wraplength=320,
        )
        self.path_label.grid(row=2, column=0, pady=(0, 10))

        # 浏览按钮
        self.browse_btn = ttk.Button(
            self,
            text="浏览文件...",
            command=self._browse_file,
        )
        self.browse_btn.grid(row=3, column=0)

        # 绑定拖拽事件 (Windows 上可通过 tkinterdnd2 扩展支持)
        # 此处用按钮替代拖拽

    def _browse_file(self):
        """打开文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择 FBX 模型文件",
            filetypes=[
                ("FBX Model", "*.fbx *.FBX"),
                ("All supported", "*.fbx *.FBX *.obj *.obj *.glb *.gltf"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.set_file(Path(file_path))

    def set_file(self, path: Path):
        """设置选中的文件"""
        if not path.exists():
            return

        ext = path.suffix.lower()
        if ext not in self.accept_extensions:
            self.path_var.set(f"[!] 不支持的文件格式: {ext}")
            self.path_label.configure(style="Warning.TLabel")
            return

        self._current_path = path
        self.path_var.set(str(path))
        self.path_label.configure(style="Success.TLabel")
        self.icon_label.configure(text="[OK]")

        if self.on_file_selected:
            self.on_file_selected(path)

    def get_file(self) -> Path | None:
        return self._current_path

    def clear(self):
        self._current_path = None
        self.path_var.set("")
        self.path_label.configure(style="Muted.TLabel")
        self.icon_label.configure(text="[F]")


class LogPanel(ttk.Frame):
    """
    日志输出面板 — 实时显示操作日志。
    支持自动滚动到最新，颜色标记。
    """

    TAG_MAP = {
        "INFO": None,
        "SUCCESS": "success",
        "WARNING": "warning",
        "ERROR": "error",
        "ACCENT": "accent",
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 创建文本框
        self.text = tk.Text(
            self,
            wrap="word",
            state="disabled",
            bg="#0d1117",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=8,
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        # 滚动条
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

        # 颜色配置
        self.text.tag_configure("success", foreground="#2ecc71")
        self.text.tag_configure("warning", foreground="#f39c12")
        self.text.tag_configure("error", foreground="#e74c3c")
        self.text.tag_configure("accent", foreground="#e94560")
        self.text.tag_configure("header", foreground="#e94560", font=("Consolas", 10, "bold"))
        self.text.tag_configure("dim", foreground="#6c6c80")

    def log(self, message: str, tag: str = None):
        """添加一条日志"""
        self.text.configure(state="normal")

        # 自动检测消息类型
        if tag is None:
            if message.startswith("[OK]") or message.startswith("✔"):
                tag = "success"
            elif message.startswith("[!]") or message.startswith("[!]"):
                tag = "warning"
            elif message.startswith("[X]") or message.startswith("✖"):
                tag = "error"
            elif message.startswith("=" * 5):
                tag = "header"

        self.text.insert("end", message + "\n", tag or ())
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def copy_log(self):
        """复制日志到剪贴板"""
        content = self.text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)


class ToolStatusBar(ttk.Frame):
    """底部状态栏 — 显示当前状态和进度"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(relief="sunken", borderwidth=1)

        # 状态文本
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            style="Muted.TLabel",
            font=("", 9),
        )
        self.status_label.pack(side="left", padx=10, pady=2)

        # 进度条
        self.progress = ttk.Progressbar(
            self,
            mode="determinate",
            length=150,
        )
        self.progress.pack(side="right", padx=10, pady=2)

    def set_status(self, text: str, progress: float = None):
        self.status_var.set(text)
        if progress is not None:
            self.progress["value"] = progress

    def set_indeterminate(self, active: bool = True):
        self.progress["mode"] = "indeterminate" if active else "determinate"
        if active:
            self.progress.start()
        else:
            self.progress.stop()

    def reset(self):
        self.status_var.set("就绪")
        self.progress["value"] = 0
        self.progress["mode"] = "determinate"
        self.progress.stop()


class FileListFrame(ttk.Frame):
    """
    文件列表框架 — 显示 .pak 文件列表，带复选框和多选支持。
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 标题栏
        self.header = ttk.Label(self, text="[*] 发现以下 .pak 文件：", style="Heading.TLabel")
        self.header.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # 列表框
        self.listbox = tk.Listbox(
            self,
            selectmode="extended",
            bg="#1e2a4a",
            fg="#e8e8e8",
            selectbackground="#e94560",
            selectforeground="white",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            height=12,
        )
        self.listbox.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # 底部信息栏
        self.info_var = tk.StringVar(value="共 0 个文件")
        self.info_label = ttk.Label(self, textvariable=self.info_var, style="Muted.TLabel")
        self.info_label.grid(row=2, column=0, sticky="w", pady=(5, 0))

    def add_files(self, files: list):
        """添加文件到列表"""
        for f in files:
            display = f"{f['name']:60s} {f['size_mb']:>8.1f} MB"
            self.listbox.insert("end", display)
        self.info_var.set(f"共 {self.listbox.size()} 个文件")

    def clear(self):
        self.listbox.delete(0, "end")
        self.info_var.set("共 0 个文件")

    def get_selected_indices(self) -> list[int]:
        """获取选中项的索引"""
        return self.listbox.curselection()

    def get_all_items(self) -> list[str]:
        """获取所有列表项的文本"""
        return [self.listbox.get(i) for i in range(self.listbox.size())]
