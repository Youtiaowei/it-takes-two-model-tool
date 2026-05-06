from __future__ import annotations
"""向导页面 — 每个步骤对应一个页面"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Callable

from config import config
from scanner import GameScanner, ScanResult, PakFileInfo
from ui.widgets import DropZone, LogPanel, FileListFrame, ToolStatusBar
from ui.theme import apply_ttk_styles


class BasePage(ttk.Frame):
    """所有页面的基类"""

    PAGE_ID = "base"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._setup_ui()

    def _setup_ui(self):
        """子类覆盖此方法构建界面"""
        pass

    def on_enter(self):
        """每当切换到该页面时调用"""
        pass

    def on_exit(self):
        """离开该页面时调用"""
        pass


class ScanPage(BasePage):
    """
    第1步：扫描页面
    自动扫描游戏目录和 .pak 文件，或手动指定路径。
    """

    PAGE_ID = "scan"

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ──── 标题 ────
        title = ttk.Label(
            self, text="[>] 第1步：扫描游戏资源",
            style="Title.TLabel"
        )
        title.grid(row=0, column=0, pady=(0, 5), sticky="w")

        subtitle = ttk.Label(
            self,
            text="自动检测《双人成行》安装目录，扫描所有 .pak 资源文件",
            style="Muted.TLabel",
        )
        subtitle.grid(row=1, column=0, pady=(0, 15), sticky="w")

        # ──── 主内容区 ────
        main_frame = ttk.Frame(self)
        main_frame.grid(row=2, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # 操作栏
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        action_frame.grid_columnconfigure(2, weight=1)

        self.scan_btn = ttk.Button(
            action_frame,
            text="[>] 开始扫描",
            command=self._do_scan,
            style="Accent.TButton",
        )
        self.scan_btn.grid(row=0, column=0, padx=(0, 8))

        self.manual_btn = ttk.Button(
            action_frame,
            text="[F] 手动选择目录",
            command=self._manual_select,
        )
        self.manual_btn.grid(row=0, column=1, padx=(0, 8))

        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(
            action_frame,
            textvariable=self.status_var,
            style="Muted.TLabel",
        )
        self.status_label.grid(row=0, column=2, sticky="e")

        # 文件列表
        self.file_list = FileListFrame(main_frame)
        self.file_list.grid(row=1, column=0, sticky="nsew")

        # 游戏路径显示
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        path_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(path_frame, text="游戏目录:", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.path_var = tk.StringVar(value="未检测")
        ttk.Label(path_frame, textvariable=self.path_var, style="Card.TLabel").grid(
            row=0, column=1, sticky="w", padx=(8, 0)
        )

        # 日志面板
        self.log = LogPanel(main_frame)
        self.log.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        self.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)

    def _do_scan(self):
        """执行扫描"""
        self.scan_btn.configure(state="disabled")
        self.log.clear()
        self.file_list.clear()
        self.log.log("[>] 正在扫描...", "header")

        scanner = GameScanner(progress_callback=lambda msg: self.log.log(msg))
        result = scanner.full_scan()

        # 更新界面
        if result.game_found:
            self.path_var.set(str(result.game_dir))
            config.game_path = str(result.game_dir)
        else:
            self.path_var.set("未找到，请手动选择")

        # 显示 .pak 文件
        if result.pak_files:
            files_data = [
                {"name": p.name, "size_mb": p.size_mb}
                for p in result.pak_files[:20]  # 最多显示20个
            ]
            self.file_list.add_files(files_data)
            self.log.log(f"\n[*] 发现 {len(result.pak_files)} 个 .pak 文件", "header")

            # 显示角色相关文件
            char_paks = scanner.find_character_paks(result.pak_files)
            if char_paks:
                self.log.log("\n[G] 角色相关文件：")
                for char_name, paks in char_paks.items():
                    self.log.log(f"  {char_name}: {', '.join(p.name for p in paks)}")

        # 工具检测
        if result.unrealpak_tool:
            config.unrealpak_path = str(result.unrealpak_tool)
        if result.blender_tool:
            config.blender_path = str(result.blender_tool)

        # 存储扫描结果供后续页面使用
        self.app.scan_result = result

        self.status_var.set(f"扫描完成 — {len(result.pak_files)} 个 .pak 文件")
        self.scan_btn.configure(state="normal")

        self.log.log("\n[OK] 扫描完成！请进入下一步", "header")

    def _manual_select(self):
        """手动选择游戏目录"""
        dir_path = filedialog.askdirectory(title="选择《双人成行》游戏目录")
        if not dir_path:
            return

        path = Path(dir_path)
        self.log.clear()
        self.log.log(f"[F] 手动选择: {path}")

        # 检查目录有效性
        from utils.path_utils import _validate_game_dir, find_pak_files
        if _validate_game_dir(path):
            self.path_var.set(str(path.resolve()))
            config.game_path = str(path.resolve())
            self.log.log("[OK] 有效的游戏目录")

            # 扫描 .pak
            paks = find_pak_files(path)
            if paks:
                files_data = [
                    {"name": p.name, "size_mb": p.stat().st_size / (1024 * 1024)}
                    for p in paks[:20]
                ]
                self.file_list.add_files(files_data)
                self.log.log(f"[*] 发现 {len(paks)} 个 .pak 文件")

                # 更新扫描结果
                result = ScanResult()
                result.game_dir = path.resolve()
                result.game_found = True
                result.pak_files = [
                    PakFileInfo(path=p) for p in paks
                ]
                self.app.scan_result = result
            else:
                self.log.log("[!] 未找到 .pak 文件")
        else:
            self.path_var.set("[X] 无效的游戏目录")
            self.log.log("[X] 该目录没有包含 .pak 文件，请确认选择了正确的游戏目录")


class UnpackPage(BasePage):
    """
    第2步：解包页面
    选择要解包的 .pak 文件，指定输出目录，执行解包。
    """

    PAGE_ID = "unpack"

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self, text="[*] 第2步：解包资源文件", style="Title.TLabel")
        title.grid(row=0, column=0, pady=(0, 5), sticky="w")

        subtitle = ttk.Label(
            self,
            text="选择要解包的 .pak 文件，提取其中的模型、贴图等资源",
            style="Muted.TLabel",
        )
        subtitle.grid(row=1, column=0, pady=(0, 15), sticky="w")

        # 主内容
        main_frame = ttk.Frame(self)
        main_frame.grid(row=2, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # 左侧：.pak 列表
        list_frame = ttk.LabelFrame(main_frame, text=".pak 文件列表", padding=8)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.pak_listbox = tk.Listbox(
            list_frame, selectmode="single",
            bg="#1e2a4a", fg="#e8e8e8",
            selectbackground="#e94560",
            relief="flat", borderwidth=0,
            font=("Consolas", 10),
        )
        self.pak_listbox.grid(row=0, column=0, sticky="nsew")

        # 右侧：操作区
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)

        # 输出目录
        ttk.Label(right_frame, text="解包输出目录:", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        out_frame = ttk.Frame(right_frame)
        out_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        out_frame.grid_columnconfigure(0, weight=1)

        self.out_path_var = tk.StringVar(value=str(Path.home() / "it-takes-two-output"))
        self.out_entry = ttk.Entry(out_frame, textvariable=self.out_path_var)
        self.out_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.browse_out_btn = ttk.Button(
            out_frame, text="浏览...", command=self._browse_output
        )
        self.browse_out_btn.grid(row=0, column=1)

        # 解包按钮
        self.unpack_btn = ttk.Button(
            right_frame, text="[/] 开始解包",
            command=self._do_unpack, style="Accent.TButton",
        )
        self.unpack_btn.grid(row=2, column=0, pady=(0, 10))

        # 工具状态
        self.tool_status_var = tk.StringVar(value="")
        ttk.Label(right_frame, textvariable=self.tool_status_var,
                  style="Warning.TLabel").grid(row=3, column=0, sticky="w")

        # 日志
        self.log = LogPanel(right_frame)
        self.log.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        right_frame.grid_rowconfigure(4, weight=1)

    def on_enter(self):
        """进入页面时刷新 .pak 列表"""
        self._refresh_pak_list()
        self._check_tools()

    def _refresh_pak_list(self):
        self.pak_listbox.delete(0, "end")
        result = getattr(self.app, "scan_result", None)
        if result and result.pak_files:
            for p in result.pak_files:
                self.pak_listbox.insert("end", f"{p.name:50s} {p.size_mb:>8.1f} MB")

    def _check_tools(self):
        from utils.path_utils import find_unrealpak_tool
        upak = config.unrealpak_path or find_unrealpak_tool()
        if upak and Path(upak).exists():
            self.tool_status_var.set("[OK] UnrealPak 就绪")
        else:
            self.tool_status_var.set("[!] 未找到 UnrealPak，请在设置中指定路径")

    def _browse_output(self):
        path = filedialog.askdirectory(title="选择解包输出目录")
        if path:
            self.out_path_var.set(path)

    def _do_unpack(self):
        selection = self.pak_listbox.curselection()
        if not selection:
            self.log.log("[!] 请先选择一个 .pak 文件")
            return

        result = getattr(self.app, "scan_result", None)
        if not result:
            self.log.log("[X] 未找到扫描结果，请先完成第1步")
            return

        pak_path = result.pak_files[selection[0]].path
        out_dir = Path(self.out_path_var.get())

        from unpacker import Unpacker
        upak_path = config.unrealpak_path
        unpacker = Unpacker(
            unrealpak_path=upak_path or None,
            callback=lambda msg: self.log.log(msg),
        )

        self.unpack_btn.configure(state="disabled")
        self.log.clear()
        self.log.log(f"[*] 开始解包: {pak_path.name}", "header")

        success = unpacker.unpack(pak_path, out_dir)

        if success:
            # 保存解包目录供后续步骤使用
            self.app.unpacked_dir = out_dir
            self.log.log("\n[OK] 解包完成！可以进入下一步", "header")

        self.unpack_btn.configure(state="normal")


class ReplacePage(BasePage):
    """
    第3步：模型替换页面
    选择角色、导入 FBX 模型，执行替换。
    """

    PAGE_ID = "replace"

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self, text="[/] 第3步：模型替换", style="Title.TLabel")
        title.grid(row=0, column=0, pady=(0, 5), sticky="w")

        subtitle = ttk.Label(
            self,
            text="选择要替换的角色，导入 FBX 模型文件",
            style="Muted.TLabel",
        )
        subtitle.grid(row=1, column=0, pady=(0, 15), sticky="w")

        main_frame = ttk.Frame(self)
        main_frame.grid(row=2, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # 左侧：角色选择
        left_frame = ttk.LabelFrame(main_frame, text="选择角色", padding=12)
        left_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))

        from model_replacer import CHARACTERS
        self.char_var = tk.StringVar(value=CHARACTERS[0].id)
        for i, char in enumerate(CHARACTERS):
            rb = ttk.Radiobutton(
                left_frame,
                text=f"{char.name_cn} ({char.name_en})",
                variable=self.char_var,
                value=char.id,
            )
            rb.grid(row=i, column=0, sticky="w", pady=4)

        char_info_frame = ttk.Frame(left_frame)
        char_info_frame.grid(row=len(CHARACTERS) + 1, column=0, sticky="ew", pady=(15, 0))
        self.char_info_var = tk.StringVar(value=CHARACTERS[0].notes)
        ttk.Label(char_info_frame, textvariable=self.char_info_var,
                  style="Muted.TLabel", wraplength=180).pack()

        # 右侧：文件选择和操作
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)

        # FBX 拖拽区
        self.drop_zone = DropZone(
            right_frame,
            text="拖拽 FBX 文件到此处，或点击浏览",
            on_file_selected=self._on_fbx_selected,
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        # 选项
        opts_frame = ttk.LabelFrame(right_frame, text="选项", padding=10)
        opts_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        opts_frame.grid_columnconfigure(0, weight=1)

        self.auto_retarget_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opts_frame, text="自动骨骼重定向（推荐）",
            variable=self.auto_retarget_var,
        ).grid(row=0, column=0, sticky="w", pady=2)

        self.match_mat_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opts_frame, text="自动材质匹配（推荐）",
            variable=self.match_mat_var,
        ).grid(row=1, column=0, sticky="w", pady=2)

        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opts_frame, text="替换前自动备份",
            variable=self.auto_backup_var,
        ).grid(row=2, column=0, sticky="w", pady=2)

        # 操作按钮
        self.replace_btn = ttk.Button(
            right_frame,
            text="[B] 执行替换",
            command=self._do_replace,
            style="Accent.TButton",
        )
        self.replace_btn.grid(row=2, column=0, pady=(0, 5))

        self.preview_btn = ttk.Button(
            right_frame,
            text="[V] 预览骨架",
            command=self._preview_skeleton,
        )
        self.preview_btn.grid(row=3, column=0, pady=(0, 10))

        # 日志
        self.log = LogPanel(main_frame)
        self.log.grid(row=1, column=1, sticky="nsew", pady=(10, 0))
        main_frame.grid_rowconfigure(1, weight=1)

    def _on_fbx_selected(self, path: Path):
        self.log.clear()
        self.log.log(f"[*] 已选择模型: {path}")
        self.log.log(f"   大小: {path.stat().st_size / 1024:.1f} KB")

        # 更新选中的角色信息
        from model_replacer import CHARACTERS
        char_id = self.char_var.get()
        char = next((c for c in CHARACTERS if c.id == char_id), None)
        if char:
            self.char_info_var.set(char.notes)

    def _preview_skeleton(self):
        fbx_path = self.drop_zone.get_file()
        if not fbx_path:
            self.log.log("[!] 请先选择一个 FBX 文件")
            return

        from model_replacer import ModelReplacer
        replacer = ModelReplacer(
            blender_path=config.blender_path,
            callback=lambda msg: self.log.log(msg),
        )

        self.log.log("[V] 正在预览骨架...")
        result = replacer.preview_skeleton(fbx_path)
        if result:
            for arm in result.get("armatures", []):
                self.log.log(f"  骨架: {arm['name']} ({arm['bone_count']} 根骨骼)")
        else:
            self.log.log("[!] 无法预览骨架，请检查 Blender 配置")

    def _do_replace(self):
        fbx_path = self.drop_zone.get_file()
        if not fbx_path:
            self.log.log("[!] 请先选择一个 FBX 模型文件")
            return

        char_id = self.char_var.get()
        from model_replacer import ReplacementConfig, ModelReplacer, CHARACTERS

        char = next((c for c in CHARACTERS if c.id == char_id), None)
        if not char:
            self.log.log("[X] 无效的角色选择")
            return

        config_replacement = ReplacementConfig(
            character_id=char_id,
            fbx_path=fbx_path,
            auto_retarget=self.auto_retarget_var.get(),
            match_materials=self.match_mat_var.get(),
            backup_first=self.auto_backup_var.get(),
        )

        errors = config_replacement.validate()
        if errors:
            for err in errors:
                self.log.log(f"[X] {err}")
            return

        replacer = ModelReplacer(
            blender_path=config.blender_path,
            callback=lambda msg: self.log.log(msg),
        )

        self.replace_btn.configure(state="disabled")
        self.log.clear()
        self.log.log(f"[->] 开始替换: {char.name_cn}", "header")

        unpacked_dir = getattr(self.app, "unpacked_dir", None)
        success = replacer.replace_character(config_replacement, unpacked_dir)

        if success:
            self.log.log("\n[OK] 模型替换完成！请进入下一步封包", "header")
        else:
            self.log.log("\n[!] 替换未完成，请参考上方指引操作")

        self.replace_btn.configure(state="normal")


class RepackPage(BasePage):
    """
    第4步：封包页面
    将修改后的资源重新打包为 .pak，自动备份并替换原文件。
    """

    PAGE_ID = "repack"

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self, text="[*] 第4步：资源封包", style="Title.TLabel")
        title.grid(row=0, column=0, pady=(0, 5), sticky="w")

        subtitle = ttk.Label(
            self,
            text="将修改后的资源重新打包，备份并替换游戏文件",
            style="Muted.TLabel",
        )
        subtitle.grid(row=1, column=0, pady=(0, 15), sticky="w")

        main_frame = ttk.Frame(self)
        main_frame.grid(row=2, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)

        # 源目录
        ttk.Label(main_frame, text="修改后的资源目录:", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        src_frame = ttk.Frame(main_frame)
        src_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        src_frame.grid_columnconfigure(0, weight=1)

        self.src_var = tk.StringVar(value=str(Path.home() / "it-takes-two-output"))
        ttk.Entry(src_frame, textvariable=self.src_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(src_frame, text="浏览...", command=self._browse_src).grid(row=0, column=1)

        # 原始 .pak 路径
        ttk.Label(main_frame, text="原始 .pak 文件:", style="Heading.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        pak_frame = ttk.Frame(main_frame)
        pak_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        pak_frame.grid_columnconfigure(0, weight=1)

        self.pak_var = tk.StringVar(value="")
        ttk.Entry(pak_frame, textvariable=self.pak_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(pak_frame, text="选择...", command=self._browse_pak).grid(row=0, column=1)

        # 操作区
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.repack_btn = ttk.Button(
            action_frame, text="[B] 开始封包",
            command=self._do_repack, style="Accent.TButton",
        )
        self.repack_btn.grid(row=0, column=0, padx=(0, 8))

        self.restore_btn = ttk.Button(
            action_frame, text="[R] 恢复备份",
            command=self._do_restore,
        )
        self.restore_btn.grid(row=0, column=1, padx=(0, 8))

        self.backup_info_var = tk.StringVar(value="")
        ttk.Label(action_frame, textvariable=self.backup_info_var,
                  style="Muted.TLabel").grid(row=0, column=2, sticky="e", padx=(20, 0))

        # 日志
        self.log = LogPanel(main_frame)
        self.log.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        main_frame.grid_rowconfigure(5, weight=1)

        # 预填原始 .pak
        self._auto_fill_pak()

    def _browse_src(self):
        path = filedialog.askdirectory(title="选择修改后的资源目录")
        if path:
            self.src_var.set(path)

    def _browse_pak(self):
        path = filedialog.askopenfilename(
            title="选择原始 .pak 文件",
            filetypes=[("Pak files", "*.pak"), ("All files", "*.*")],
        )
        if path:
            self.pak_var.set(path)

    def _auto_fill_pak(self):
        """自动填充原始 .pak 文件路径"""
        result = getattr(self.app, "scan_result", None)
        if result and result.pak_files:
            # 选择最大的非加密文件
            candidates = [p for p in result.pak_files if not p.is_encrypted]
            if candidates:
                self.pak_var.set(str(candidates[0].path))

    def _do_repack(self):
        src_dir = Path(self.src_var.get())
        pak_path = Path(self.pak_var.get())

        if not src_dir.exists():
            self.log.log("[X] 资源目录不存在")
            return
        if not pak_path.exists():
            self.log.log("[X] 原始 .pak 文件不存在")
            return

        from repacker import Repacker
        repacker = Repacker(
            unrealpak_path=config.unrealpak_path or None,
            callback=lambda msg: self.log.log(msg),
        )

        self.log.clear()
        self.log.log("[*] 开始封包流程...", "header")
        self.repack_btn.configure(state="disabled")

        success = repacker.repack(
            source_dir=src_dir,
            original_pak=pak_path,
            create_backup=True,
            game_dir=Path(config.game_path) if config.game_path else None,
        )

        if success:
            self.log.log("\n[*] 全部完成！模型已成功替换到游戏中", "header")
            self.log.log("[?] 重新启动游戏即可看到效果")

        self.repack_btn.configure(state="normal")

    def _do_restore(self):
        from repacker import Repacker
        repacker = Repacker(
            unrealpak_path=config.unrealpak_path,
            callback=lambda msg: self.log.log(msg),
        )

        self.log.log("[R] 正在恢复备份...", "header")
        success = repacker.restore_original()
        if success:
            self.log.log("[OK] 已恢复到修改前的状态")


class SettingsPage(BasePage):
    """
    设置页面 — 工具路径、主题、语言等配置。
    """

    PAGE_ID = "settings"

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ttk.Label(self, text="[=] 设置", style="Title.TLabel")
        title.grid(row=0, column=0, pady=(0, 15), sticky="w")

        # 滚动内容区
        canvas = tk.Canvas(self, bg="#1a1a2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.grid_columnconfigure(0, weight=1)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        row = 0

        # ──── 游戏路径 ────
        frame1 = ttk.LabelFrame(scroll_frame, text="游戏目录", padding=12)
        frame1.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame1.grid_columnconfigure(1, weight=1)
        row += 1

        self.game_path_var = tk.StringVar(value=config.game_path)
        ttk.Entry(frame1, textvariable=self.game_path_var).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5)
        )
        ttk.Button(frame1, text="浏览...", command=self._browse_game).grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        ttk.Button(frame1, text="自动检测", command=self._auto_detect_game).grid(
            row=1, column=1, sticky="w"
        )

        # ──── UnrealPak 路径 ────
        frame2 = ttk.LabelFrame(scroll_frame, text="UnrealPak 工具路径", padding=12)
        frame2.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame2.grid_columnconfigure(1, weight=1)
        row += 1

        self.upak_var = tk.StringVar(value=config.unrealpak_path)
        ttk.Entry(frame2, textvariable=self.upak_var).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5)
        )
        ttk.Button(frame2, text="浏览...", command=self._browse_upak).grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        ttk.Button(frame2, text="自动查找", command=self._auto_find_upak).grid(
            row=1, column=1, sticky="w"
        )

        # ──── Blender 路径 ────
        frame3 = ttk.LabelFrame(scroll_frame, text="Blender 路径（可选）", padding=12)
        frame3.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame3.grid_columnconfigure(1, weight=1)
        row += 1

        self.blender_var = tk.StringVar(value=config.blender_path)
        ttk.Entry(frame3, textvariable=self.blender_var).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5)
        )
        ttk.Button(frame3, text="浏览...", command=self._browse_blender).grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        ttk.Button(frame3, text="自动查找", command=self._auto_find_blender).grid(
            row=1, column=1, sticky="w"
        )

        # ──── 主题 ────
        frame4 = ttk.LabelFrame(scroll_frame, text="外观", padding=12)
        frame4.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        row += 1

        self.theme_var = tk.StringVar(value=config.get("theme", "dark"))
        ttk.Radiobutton(frame4, text="[D] 暗色主题", variable=self.theme_var,
                        value="dark").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Radiobutton(frame4, text="[L] 亮色主题", variable=self.theme_var,
                        value="light").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Button(frame4, text="应用主题", command=self._apply_theme).grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )

        # ──── 保存 ────
        save_btn = ttk.Button(
            scroll_frame, text="[S] 保存设置",
            command=self._save_settings, style="Accent.TButton",
        )
        save_btn.grid(row=row, column=0, pady=(10, 0))

    def _browse_game(self):
        path = filedialog.askdirectory(title="选择《双人成行》游戏目录")
        if path:
            self.game_path_var.set(path)

    def _browse_upak(self):
        path = filedialog.askopenfilename(
            title="选择 UnrealPak 可执行文件",
            filetypes=[("Executable", "UnrealPak* UnrealPak.exe"), ("All files", "*.*")],
        )
        if path:
            self.upak_var.set(path)

    def _browse_blender(self):
        path = filedialog.askopenfilename(
            title="选择 Blender 可执行文件",
            filetypes=[("Executable", "blender* blender.exe"), ("All files", "*.*")],
        )
        if path:
            self.blender_var.set(path)

    def _auto_detect_game(self):
        from utils.path_utils import find_game_installation
        path = find_game_installation()
        if path:
            self.game_path_var.set(str(path))
        else:
            from ui.theme import AVAILABLE_THEMES
            theme = AVAILABLE_THEMES.get(config.get("theme", "dark"))
            self.master.log.log("[!] 未自动检测到游戏目录，请手动选择")

    def _auto_find_upak(self):
        from utils.path_utils import find_unrealpak_tool
        path = find_unrealpak_tool()
        if path:
            self.upak_var.set(str(path))

    def _auto_find_blender(self):
        from utils.path_utils import find_blender
        path = find_blender()
        if path:
            self.blender_var.set(str(path))

    def _apply_theme(self):
        from ui.theme import AVAILABLE_THEMES
        theme = AVAILABLE_THEMES.get(self.theme_var.get())
        if theme:
            apply_ttk_styles(self.app.master, theme)
            config.set("theme", theme.name)

    def _save_settings(self):
        config.game_path = self.game_path_var.get()
        config.unrealpak_path = self.upak_var.get()
        config.blender_path = self.blender_var.get()
        config.set("theme", self.theme_var.get())
        from ui.theme import AVAILABLE_THEMES
        theme = AVAILABLE_THEMES.get(self.theme_var.get(), AVAILABLE_THEMES["dark"])
        apply_ttk_styles(self.app.master, theme)
        self.master.log.log("[OK] 设置已保存")
