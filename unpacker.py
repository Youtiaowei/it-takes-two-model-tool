from __future__ import annotations
"""资源解包模块 — 封装 UnrealPak 调用"""

import logging
import shlex
import subprocess
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


class Unpacker:
    """
    UnrealPak 解包封装器。
    解包 .pak 文件到指定目录，支持进度反馈。
    """

    def __init__(
        self,
        unrealpak_path: Path | str | None = None,
        callback: Callable[[str], None] | None = None,
    ):
        self.unrealpak_path = Path(unrealpak_path) if unrealpak_path else None
        self.callback = callback or (lambda msg: None)

    @property
    def is_ready(self) -> bool:
        """检查 UnrealPak 工具是否就绪"""
        if not self.unrealpak_path:
            return False
        return self.unrealpak_path.exists()

    def unpack(self, pak_file: Path, output_dir: Path) -> bool:
        """
        解包一个 .pak 文件到指定目录。
        返回是否成功。
        """
        if not self.is_ready:
            self.callback(
                "[X] UnrealPak 工具未就绪！\n\n"
                "请手动指定 UnrealPak 路径：\n"
                "  1. 安装 Unreal Engine 4.26/4.27\n"
                "  2. 定位 Engine/Binaries/Platform/UnrealPak\n"
                "  3. 在设置中指定工具路径"
            )
            return False

        if not pak_file.exists():
            self.callback(f"[X] 文件不存在: {pak_file}")
            return False

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(self.unrealpak_path),
            str(pak_file.resolve()),
            "-Extract",
            str(output_dir.resolve()),
        ]

        self.callback(f"[*] 正在解包: {pak_file.name}")
        self.callback(f"   输出目录: {output_dir}")
        self.callback(f"   命令: {' '.join(shlex.quote(c) for c in cmd)}")
        self.callback("   这可能需要几分钟，请耐心等待...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 分钟超时
            )

            if result.returncode == 0:
                self.callback(f"[OK] 解包完成！输出到: {output_dir}")
                # 简要列出内容结构
                self._summarize_contents(output_dir)
                return True
            else:
                self.callback(f"[X] 解包失败 (返回码: {result.returncode})")
                self._show_unrealpak_errors(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            self.callback("[!] 解包超时（超过 10 分钟）")
            self.callback("提示：大文件解包需要更多时间，或检查磁盘空间")
            return False
        except FileNotFoundError:
            self.callback(f"[X] 无法执行 UnrealPak: 文件不存在于 {self.unrealpak_path}")
            self.callback("请在设置中重新指定 UnrealPak 路径")
            return False
        except Exception as e:
            self.callback(f"[X] 解包异常: {e}")
            return False

    def list_pak_contents(self, pak_file: Path) -> list[str]:
        """
        列出 .pak 文件中的内容清单。
        使用 UnrealPak -List 参数。
        """
        if not self.is_ready:
            return ["[X] UnrealPak 工具未就绪"]

        cmd = [
            str(self.unrealpak_path),
            str(pak_file.resolve()),
            "-List",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return result.stdout.splitlines()
            else:
                return [f"[X] 列出内容失败: {result.stderr[:200]}"]
        except Exception as e:
            return [f"[X] 异常: {e}"]

    def _summarize_contents(self, output_dir: Path):
        """简要总结解包后的内容结构"""
        dirs = sorted(
            [d for d in output_dir.iterdir() if d.is_dir()],
            key=lambda d: sum(f.stat().st_size for f in d.rglob("*")),
            reverse=True,
        )

        top_dirs = dirs[:10]
        self.callback(f"\n[F] 解包内容概览（按大小排序）：")
        for d in top_dirs:
            size_mb = sum(f.stat().st_size for f in d.rglob("*")) / (1024 * 1024)
            self.callback(f"  {d.name}/ — {size_mb:.1f} MB")

        # 查找模型文件
        models = list(output_dir.rglob("*.uasset"))
        skeletons = list(output_dir.rglob("*Skeleton*.uasset"))
        meshes = list(output_dir.rglob("*Mesh*.uasset"))

        self.callback(f"\n[>] 检测到可能的模型资源：")
        self.callback(f"  网格体文件 (.uasset): {len(models)} 个")
        self.callback(f"  骨骼文件 (Skeleton): {len(skeletons)} 个")
        self.callback(f"  网格体文件 (Mesh): {len(meshes)} 个")

    def _show_unrealpak_errors(self, stderr: str):
        """显示 UnrealPak 错误并给出中文指引"""
        errors = stderr[:500] if stderr else "无错误输出"
        self.callback(f"  错误详情: {errors}")
        self.callback("\n[?] 常见问题：")
        self.callback("  1. .pak 文件可能已加密 → 需要先解密")
        self.callback("  2. UnrealPak 版本可能不兼容 → 尝试 UE 4.26 的版本")
        self.callback("  3. .pak 可能正在被游戏占用 → 关闭游戏后重试")
        self.callback("  4. 磁盘空间不足 → 确认有足够空间（至少 20GB）")


def unpack_preview(pak_file: Path, output_dir: Path) -> str:
    """
    快速预览解包内容（不实际解包全部）。
    返回内容列表的摘要。
    """
    return f"预览功能需要在设置中指定 UnrealPak 路径后使用"
