from __future__ import annotations
"""资源封包模块 — 将修改后的资源重新打包成 .pak，并自动备份替换"""

import logging
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from backup_manager import BackupManager

logger = logging.getLogger(__name__)


class Repacker:
    """
    资源封包引擎。
    支持：
    - 将修改后的资源目录重新打包为 .pak
    - 自动备份原始 .pak 文件
    - 替换游戏目录中的原文件
    """

    def __init__(
        self,
        unrealpak_path: Path | str | None = None,
        callback: Callable[[str], None] | None = None,
    ):
        self.unrealpak_path = Path(unrealpak_path) if unrealpak_path else None
        self.callback = callback or (lambda msg: None)
        self.backup_mgr = BackupManager()

    @property
    def is_ready(self) -> bool:
        if not self.unrealpak_path:
            return False
        return self.unrealpak_path.exists()

    def repack(
        self,
        source_dir: Path,
        original_pak: Path,
        output_pak: Path | None = None,
        create_backup: bool = True,
        game_dir: Path | None = None,
    ) -> bool:
        """
        完整封包流程：
        1. 验证输入
        2. 生成封包清单 (filelist.txt)
        3. 调用 UnrealPak 打包
        4. 备份原始文件
        5. 替换游戏目录中的 .pak
        """
        if not self.is_ready:
            self.callback(
                "[X] UnrealPak 工具未就绪！\n\n"
                "请先在设置中指定 UnrealPak 路径。"
            )
            return False

        if not source_dir.exists():
            self.callback(f"[X] 源目录不存在: {source_dir}")
            return False

        if not original_pak.exists():
            self.callback(f"[X] 原始 .pak 文件不存在: {original_pak}")
            return False

        # 确定输出路径
        output_pak = output_pak or original_pak
        self.callback(f"[*] 开始封包流程")
        self.callback(f"  源目录: {source_dir}")
        self.callback(f"  原始 .pak: {original_pak}")
        self.callback(f"  输出 .pak: {output_pak}")

        # ──── 第1步: 生成封包清单 ────
        self.callback("[W] 正在生成文件清单...")
        filelist_path = self._generate_filelist(source_dir)
        if not filelist_path:
            self.callback("[X] 生成文件清单失败")
            return False

        # ──── 第2步: 执行封包 ────
        self.callback("[B] 正在打包资源（这可能需要几分钟）...")
        success = self._run_repack(filelist_path, output_pak)
        if not success:
            self.callback("[X] 封包失败")
            self.callback("[?] 可能的原因：")
            self.callback("  1. 文件清单格式错误")
            self.callback("  2. 磁盘空间不足")
            self.callback("  3. UnrealPak 版本不兼容")
            return False

        # ──── 第3步: 备份 ────
        if create_backup:
            self.callback("[S] 正在备份原始文件...")
            record = self.backup_mgr.create_backup(
                source_paths=[original_pak],
                description=f"替换前备份: {original_pak.name}",
                callback=self.callback,
            )
            self.callback(f"  备份 ID: {record.id}")

        # ──── 第4步: 替换 ────
        if output_pak.resolve() != original_pak.resolve():
            self.callback(f"[L] 正在替换游戏目录中的 .pak 文件...")
            try:
                shutil.copy2(output_pak, original_pak)
                self.callback(f"[OK] 已替换: {original_pak}")
            except PermissionError:
                self.callback(f"[X] 文件被占用，无法替换")
                self.callback(f"[?] 请关闭游戏和 Steam 后重试")
                return False
            except Exception as e:
                self.callback(f"[X] 替换失败: {e}")
                return False

        self.callback("=" * 50)
        self.callback("[OK] 封包与替换全部完成！")
        self.callback(f"  输出文件: {output_pak}")
        self.callback(f"  如需恢复原文件，请使用备份恢复功能")
        self.callback("=" * 50)
        return True

    def restore_original(self, backup_id: str | None = None) -> bool:
        """恢复原始 .pak 文件"""
        if backup_id:
            return self.backup_mgr.restore_backup(backup_id, callback=self.callback)

        # 无指定备份时，恢复最新的
        backups = self.backup_mgr.list_backups()
        if not backups:
            self.callback("[X] 没有可用的备份")
            return False
        return self.backup_mgr.restore_backup(backups[-1].id, callback=self.callback)

    def _generate_filelist(self, source_dir: Path) -> Path | None:
        """
        生成 UnrealPak 所需的文件清单 (filelist.txt)。
        格式：
        "MountPoint/Path/File.uasset" "Absolute/Source/Path/File.uasset"
        """
        source_dir = source_dir.resolve()
        filelist_path = source_dir / "filelist.txt"

        lines = []
        mount_root = "../../../"  # UE 的 PakMountPoint 相对路径

        for file_path in sorted(source_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.name == "filelist.txt":
                continue

            # 计算挂载路径
            rel = file_path.relative_to(source_dir)
            mount_path = f"{mount_root}{rel.as_posix()}"

            lines.append(f'"{mount_path}" "{file_path}"')

        if not lines:
            self.callback("[!]  源目录中没有找到任何文件")
            return None

        # 写入文件清单
        filelist_path.write_text("\n".join(lines), encoding="utf-8")
        self.callback(f"  文件清单: {len(lines)} 条记录")
        return filelist_path

    def _run_repack(self, filelist_path: Path, output_pak: Path) -> bool:
        """调用 UnrealPak 执行封包"""
        cmd = [
            str(self.unrealpak_path),
            str(output_pak.resolve()),
            "-Create=" + str(filelist_path.resolve()),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1200,  # 20 分钟超时
            )

            if result.returncode == 0:
                size_mb = output_pak.stat().st_size / (1024 * 1024)
                self.callback(f"[OK] 封包成功！({size_mb:.1f} MB)")
                return True
            else:
                self.callback(f"[X] 封包失败 (返回码: {result.returncode})")
                if result.stderr:
                    self.callback(f"  错误: {result.stderr[:300]}")
                return False

        except subprocess.TimeoutExpired:
            self.callback("[!] 封包超时（超过 20 分钟）")
            return False
        except Exception as e:
            self.callback(f"[X] 封包异常: {e}")
            return False
