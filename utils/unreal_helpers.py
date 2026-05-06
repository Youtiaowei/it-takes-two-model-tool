from __future__ import annotations
"""Unreal Engine 格式辅助工具 — 解析 .uasset 元数据和 Pak 结构"""

import logging
import struct
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Unreal Engine Pak 文件格式常量
PAK_FILE_MAGIC = 0x5A6F6E65  # "ZONE" in little-endian


class PakHeader:
    """Unreal .pak 文件头解析"""

    def __init__(self, data: bytes):
        if len(data) < 16:
            raise ValueError("数据不足，无法解析 Pak 文件头")

        self.magic: int = struct.unpack("<I", data[0:4])[0]
        self.version: int = struct.unpack("<I", data[4:8])[0]
        self.sub_version: int = struct.unpack("<I", data[8:12])[0]
        self.index_offset: int = struct.unpack("<Q", data[12:20])[0]

    def is_valid(self) -> bool:
        """检查是否为有效的 Unreal Pak 文件"""
        return self.magic == PAK_FILE_MAGIC

    def __str__(self):
        return (f"PakHeader(magic=0x{self.magic:08X}, "
                f"version={self.version}, "
                f"sub_version={self.sub_version})")


def read_pak_header(pak_path: Path) -> PakHeader | None:
    """读取 .pak 文件头"""
    try:
        with open(pak_path, "rb") as f:
            header_data = f.read(20)
        header = PakHeader(header_data)
        if not header.is_valid():
            logger.warning(f"无效的 .pak 文件头: {pak_path}")
            return None
        return header
    except (IOError, struct.error) as e:
        logger.error(f"读取 .pak 文件头失败: {e}")
        return None


def is_uasset(file_path: Path) -> bool:
    """检查文件是否为 .uasset"""
    return file_path.suffix.lower() == ".uasset"


def compute_file_hash(file_path: Path) -> str:
    """计算文件 SHA256（用于校验）"""
    import hashlib
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
