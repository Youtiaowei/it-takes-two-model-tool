from __future__ import annotations
"""备份管理模块 — 自动备份与恢复原文件"""

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from config import BACKUP_DIR

logger = logging.getLogger(__name__)

MANIFEST_FILE = "manifest.json"


@dataclass
class BackupRecord:
    """一次备份的记录"""
    id: str
    timestamp: str
    description: str
    files: list[dict]  # [{"original": str, "backup": str, "size": int, "hash": str}, ...]
    size_bytes: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "description": self.description,
            "files": self.files,
            "size_bytes": self.size_bytes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BackupRecord":
        return cls(**d)


class BackupManager:
    """
    文件备份与恢复管理器。
    在每次修改游戏文件前自动创建备份，支持回滚。
    """

    def __init__(self, backup_root: Path = BACKUP_DIR):
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self.backup_root / MANIFEST_FILE
        self._manifest: list[dict] = self._load_manifest()

    # ──── 公开接口 ────

    def create_backup(
        self,
        source_paths: list[Path],
        description: str = "",
        callback: Callable[[str], None] | None = None,
    ) -> BackupRecord:
        """
        创建一批文件的备份。
        返回 BackupRecord。
        """
        log = callback or (lambda msg: None)

        backup_id = f"backup_{datetime.now():%Y%m%d_%H%M%S}"
        timestamp = datetime.now().isoformat()
        backup_dir = self.backup_root / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        log(f"[D] 正在备份 {len(source_paths)} 个文件到 {backup_dir}...")
        files_meta = []
        total_bytes = 0

        for src in source_paths:
            src = Path(src)
            if not src.exists():
                log(f"[!]  跳过不存在的文件: {src}")
                continue

            rel_path = src.relative_to(src.anchor) if src.is_absolute() else src.name
            dst = backup_dir / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件
            shutil.copy2(src, dst)

            # 计算校验和
            file_hash = self._hash_file(src)
            file_size = src.stat().st_size
            total_bytes += file_size

            files_meta.append({
                "original": str(src.resolve()),
                "backup": str(dst.resolve()),
                "size": file_size,
                "hash": file_hash,
            })

            log(f"  [OK] {src.name} ({file_size:,} bytes)")

        record = BackupRecord(
            id=backup_id,
            timestamp=timestamp,
            description=description or f"备份 {len(files_meta)} 个文件",
            files=files_meta,
            size_bytes=total_bytes,
        )

        self._manifest.append(record.to_dict())
        self._save_manifest()
        log(f"[OK] 备份完成！共 {len(files_meta)} 个文件 ({total_bytes / 1024:.1f} KB)")
        return record

    def restore_backup(self, backup_id: str, callback: Callable[[str], None] | None = None) -> bool:
        """
        恢复指定备份。
        返回是否成功。
        """
        log = callback or (lambda msg: None)

        record = self.get_record(backup_id)
        if not record:
            log(f"[X] 未找到备份: {backup_id}")
            return False

        log(f"[R] 正在恢复备份 {backup_id}...")
        restored = 0
        for file_info in record.files:
            backup_path = Path(file_info["backup"])
            original_path = Path(file_info["original"])

            if not backup_path.exists():
                log(f"[!]  备份文件缺失: {backup_path}")
                continue

            # 验证校验和
            current_hash = self._hash_file(backup_path)
            if current_hash != file_info["hash"]:
                log(f"[!]  备份文件校验和不匹配（可能已损坏）: {backup_path}")
                continue

            # 恢复
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, original_path)
            restored += 1
            log(f"  [OK] 已恢复: {original_path.name}")

        log(f"[OK] 恢复完成！成功恢复 {restored}/{len(record.files)} 个文件")
        return True

    def list_backups(self) -> list[BackupRecord]:
        """列出所有可用备份"""
        return [BackupRecord.from_dict(d) for d in self._manifest]

    def get_record(self, backup_id: str) -> BackupRecord | None:
        """获取单个备份记录"""
        for d in self._manifest:
            if d["id"] == backup_id:
                return BackupRecord.from_dict(d)
        return None

    def delete_backup(self, backup_id: str, callback: Callable[[str], None] | None = None) -> bool:
        """删除备份"""
        log = callback or (lambda msg: None)

        for i, d in enumerate(self._manifest):
            if d["id"] == backup_id:
                backup_dir = self.backup_root / backup_id
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                self._manifest.pop(i)
                self._save_manifest()
                log(f"[D]  已删除备份: {backup_id}")
                return True

        log(f"[X] 未找到备份: {backup_id}")
        return False

    def get_total_backup_size(self) -> int:
        """所有备份占用总字节数"""
        return sum(
            Path(self.backup_root / d["id"]).stat().st_size
            for d in self._manifest
            if (self.backup_root / d["id"]).exists()
        )

    def cleanup_old_backups(self, max_backups: int = 10):
        """清理超出数量限制的旧备份"""
        sorted_records = sorted(self._manifest, key=lambda r: r["timestamp"])
        while len(sorted_records) > max_backups:
            oldest = sorted_records.pop(0)
            self.delete_backup(oldest["id"])

    # ──── 内部方法 ────

    def _load_manifest(self) -> list[dict]:
        if self._manifest_path.exists():
            try:
                with open(self._manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_manifest(self):
        with open(self._manifest_path, "w", encoding="utf-8") as f:
            json.dump(self._manifest, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _hash_file(path: Path) -> str:
        """计算文件的 SHA256 校验和"""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
