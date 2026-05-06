from __future__ import annotations
"""扫描器模块 — 自动扫描并定位游戏资源文件"""

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from utils.path_utils import (
    find_game_installation,
    find_pak_files,
    find_unrealpak_tool,
    find_blender,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# 数据类型
# ──────────────────────────────────────────────────────────

@dataclass
class PakFileInfo:
    """单个 .pak 文件的信息"""
    path: Path
    size_mb: float = 0.0
    is_encrypted: bool = False
    is_mounted: bool = False

    def __post_init__(self):
        if self.path.exists():
            self.size_mb = round(self.path.stat().st_size / (1024 * 1024), 2)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def parent_dir(self) -> str:
        return str(self.path.parent)

    def __str__(self):
        return f"{self.name} ({self.size_mb:.1f} MB)"


@dataclass
class ScanResult:
    """一次完整扫描的结果"""
    game_dir: Path | None = None
    game_found: bool = False
    pak_files: list[PakFileInfo] = field(default_factory=list)
    unrealpak_tool: Path | None = None
    blender_tool: Path | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def total_pak_size_mb(self) -> float:
        return round(sum(p.size_mb for p in self.pak_files), 2)

    @property
    def pak_count(self) -> int:
        return len(self.pak_files)


# ──────────────────────────────────────────────────────────
# 扫描引擎
# ──────────────────────────────────────────────────────────

class GameScanner:
    """
    游戏资源扫描引擎。
    支持同步扫描和异步回调两种模式。
    """

    # 《双人成行》的角色/资源文件命名模式
    CHARACTER_PATTERNS = {
        "cody": re.compile(r"cody", re.IGNORECASE),
        "may": re.compile(r"may", re.IGNORECASE),
        "rose": re.compile(r"rose\b", re.IGNORECASE),
        "dr_hakim": re.compile(r"hakim|hakim", re.IGNORECASE),
        "book_of_love": re.compile(r"book_of_love", re.IGNORECASE),
    }

    # 关键资源 .pak 文件的命名模式（按优先级）
    PAK_PATTERNS = [
        re.compile(r"ItTakesTwo/Content/Paks/ItTakesTwo/Character.*\.pak", re.IGNORECASE),
        re.compile(r"Character.*\.pak$", re.IGNORECASE),
        re.compile(r"Global.*\.pak$", re.IGNORECASE),
        re.compile(r".*\.pak$"),  # 兜底
    ]

    def __init__(self, progress_callback: Callable[[str], None] | None = None):
        self.progress = progress_callback or (lambda msg: None)

    def full_scan(self) -> ScanResult:
        """
        执行完整系统扫描：
        1. 定位游戏安装目录
        2. 扫描 .pak 文件
        3. 查找第三方工具
        """
        result = ScanResult()
        self.progress("[>] 正在扫描游戏安装目录...")

        # 1. 定位游戏
        game_dir = find_game_installation()
        if game_dir:
            result.game_dir = game_dir
            result.game_found = True
            self.progress(f"[OK] 找到游戏目录: {game_dir}")
        else:
            self.progress("[!]  未自动找到游戏目录，请手动选择")
            result.errors.append("未找到游戏安装目录")

        # 2. 扫描 .pak 文件
        if game_dir:
            self.progress("[*] 正在扫描 .pak 资源文件...")
            raw_paks = find_pak_files(game_dir)
            # 按大小过滤：排除小于 1MB 的文件（通常是补丁或小文件）
            filtered = [p for p in raw_paks if p.stat().st_size > 1_000_000]
            for p in filtered:
                info = PakFileInfo(path=p)
                info.is_encrypted = self._check_encrypted(p)
                info.is_mounted = self._check_mounted(p)
                result.pak_files.append(info)
            self.progress(f"[OK] 找到 {len(result.pak_files)} 个 .pak 文件 (总计 {result.total_pak_size_mb:.1f} MB)")

        # 3. 查找第三方工具
        self.progress("[T] 正在查找 UnrealPak 工具...")
        result.unrealpak_tool = find_unrealpak_tool()
        if result.unrealpak_tool:
            self.progress(f"[OK] 找到 UnrealPak: {result.unrealpak_tool}")
        else:
            self.progress("[!]  未找到 UnrealPak，解包功能需要手动指定工具路径")

        self.progress("[T] 正在查找 Blender...")
        result.blender_tool = find_blender()
        if result.blender_tool:
            self.progress(f"[OK] 找到 Blender: {result.blender_tool}")
        else:
            self.progress("[!]  未找到 Blender，模型替换功能受限")

        self.progress("[OK] 扫描完成！")
        return result

    def find_character_paks(self, pak_files: list[PakFileInfo]) -> dict[str, list[PakFileInfo]]:
        """
        根据文件名模式识别角色相关的 .pak 文件。
        返回 { 角色名: [PakFileInfo, ...] } 的映射。
        """
        result = {}
        for name, pattern in self.CHARACTER_PATTERNS.items():
            matches = [p for p in pak_files if pattern.search(p.path.name)]
            if matches:
                result[name] = matches
        return result

    def get_recommended_paks(self, pak_files: list[PakFileInfo]) -> list[PakFileInfo]:
        """
        返回最可能与角色模型相关的 .pak 文件（按大小降序推荐前几个）。
        """
        # 优先选择文件名包含 Character 关键字的
        character_paks = [
            p for p in pak_files
            if re.search(r"Character", p.path.name, re.IGNORECASE)
        ]
        if character_paks:
            character_paks.sort(key=lambda p: p.size_mb, reverse=True)
            return character_paks[:5]

        # 退而求其次：返回最大的几个
        sorted_paks = sorted(pak_files, key=lambda p: p.size_mb, reverse=True)
        return sorted_paks[:5]

    def scan_single_pak(self, pak_path: Path) -> dict:
        """
        分析单个 .pak 文件的详细信息。
        注意：完整文件列表需要 UnrealPak 列出，此处只做基本分析。
        """
        info = PakFileInfo(path=pak_path)
        return {
            "path": pak_path,
            "name": pak_path.name,
            "size_mb": info.size_mb,
            "is_encrypted": self._check_encrypted(pak_path),
            "suggested_characters": self._guess_contained_characters(pak_path),
        }

    # ──── 内部辅助方法 ────

    def _check_encrypted(self, path: Path) -> bool:
        """粗略检查 .pak 文件是否加密（检查文件头）"""
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            # Unreal Pak 文件头签名: 0x5A6F6E65_41434F52_XXXXXXXX_XXXXXXXX
            # 加密的 pak 文件某些标志位不同
            return False  # 简化处理，实际需要读取 PakInfo 结构
        except (IOError, OSError):
            return False

    def _check_mounted(self, path: Path) -> bool:
        """检查 .pak 文件是否正在被游戏挂载（占用中）"""
        return False  # 跨平台实现复杂，此处作为占位

    def _guess_contained_characters(self, path: Path) -> list[str]:
        """根据文件名猜测该 .pak 包含的角色"""
        found = []
        for name, pattern in self.CHARACTER_PATTERNS.items():
            if pattern.search(path.name):
                found.append(name)
        return found


# ──── 便捷函数 ────

def quick_scan() -> ScanResult:
    """一键快速扫描"""
    scanner = GameScanner()
    return scanner.full_scan()
