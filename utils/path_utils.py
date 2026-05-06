from __future__ import annotations
"""
路径工具 — 跨平台路径检测与规范化
"""
import os
import platform
import subprocess
from pathlib import Path


SYSTEM = platform.system()


def find_game_installation() -> Path | None:
    """
    自动扫描《双人成行》游戏安装目录。
    支持 Steam、Epic Games、EA App 的常见安装路径。
    """
    candidates = _build_search_paths()
    for path in candidates:
        resolved = _validate_game_dir(path)
        if resolved:
            return resolved
    return None


def find_pak_files(game_dir: Path | str) -> list[Path]:
    """
    扫描游戏目录下所有 .pak 文件，按大小排序。
    返回路径列表。
    """
    game_dir = Path(game_dir)
    pak_files = list(game_dir.rglob("*.pak"))
    pak_files.sort(key=lambda p: p.stat().st_size, reverse=True)
    return pak_files


def find_unrealpak_tool() -> Path | None:
    """
    查找系统中可用的 UnrealPak 工具。
    优先级：
    1. 用户配置
    2. 环境变量 UNREAL_PAK
    3. 常见安装位置
    """
    # 常见 Unreal Engine 安装路径下的 UnrealPak
    search_paths = [
        # Linux
        Path.home() / ".steam/root/steamapps/common/UE_4.26/Engine/Binaries/Linux/UnrealPak",
        Path.home() / ".steam/root/steamapps/common/UE_4.27/Engine/Binaries/Linux/UnrealPak",
        Path.home() / ".steam/root/steamapps/common/Unreal Engine/UE_4.26/Engine/Binaries/Linux/UnrealPak",
        # Windows
        Path("C:/Program Files/Epic Games/UE_4.26/Engine/Binaries/Win64/UnrealPak.exe"),
        Path("C:/Program Files/Epic Games/UE_4.27/Engine/Binaries/Win64/UnrealPak.exe"),
    ]

    for path in search_paths:
        if path.exists():
            return path

    # 检查环境变量
    env_path = os.environ.get("UNREAL_PAK")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    return None


def find_blender() -> Path | None:
    """
    查找系统中安装的 Blender。
    """
    if SYSTEM == "Windows":
        candidates = [
            Path(f"C:/Program Files/Blender Foundation/Blender {v}/blender.exe")
            for v in ["4.3", "4.2", "4.1", "4.0", "3.6", "3.5", "3.4", "3.3"]
        ]
    elif SYSTEM == "Linux":
        # Linux 下尝试 which 或 snap/flatpak 路径
        try:
            result = subprocess.run(["which", "blender"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        candidates = [
            Path("/snap/bin/blender"),
            Path("/usr/bin/blender"),
            Path("/usr/local/bin/blender"),
            Path.home() / "bin/blender",
        ]
    else:  # macOS
        candidates = [
            Path("/Applications/Blender.app/Contents/MacOS/Blender"),
            Path.home() / "Applications/Blender.app/Contents/MacOS/Blender",
        ]

    for path in candidates:
        if path.exists():
            return path
    return None


def _build_search_paths() -> list[Path]:
    """构建游戏目录候选搜索路径"""
    candidates = []

    if SYSTEM == "Windows":
        # Steam 默认路径
        steam_base = Path("C:/Program Files (x86)/Steam/steamapps/common")
        candidates.append(steam_base / "It Takes Two")
        candidates.append(steam_base / "ItTakesTwo")
        # 替代驱动盘
        for drive in "DEFGH":
            p = Path(f"{drive}:/Program Files (x86)/Steam/steamapps/common/It Takes Two")
            candidates.append(p)
        # Epic Games
        epic_base = Path("C:/Program Files/Epic Games")
        candidates.append(epic_base / "ItTakesTwo")
        candidates.append(epic_base / "It Takes Two")
        # EA App
        ea_base = Path("C:/Program Files/EA Games/It Takes Two")
        candidates.append(ea_base)

    elif SYSTEM == "Linux":
        # Steam (native)
        steam_base = Path.home() / ".steam/steam/steamapps/common"
        candidates.append(steam_base / "It Takes Two")
        candidates.append(steam_base / "ItTakesTwo")
        # Steam (flatpak)
        flatpak_steam = Path.home() / ".var/app/com.valvesoftware.Steam/.steam/steam/steamapps/common"
        candidates.append(flatpak_steam / "It Takes Two")
        candidates.append(flatpak_steam / "ItTakesTwo")
        # Lutris / Heroic / Wine 常见路径
        wine_paths = [
            Path.home() / "Games/ItTakesTwo",
            Path.home() / ".wine/drive_c/Program Files (x86)/Steam/steamapps/common/It Takes Two",
            Path.home() / "GAMES/ItTakesTwo",
        ]
        candidates.extend(wine_paths)

    else:  # macOS
        steam_base = Path.home() / "Library/Application Support/Steam/steamapps/common"
        candidates.append(steam_base / "It Takes Two")

    return candidates


def _validate_game_dir(path: Path) -> Path | None:
    """
    验证目录是否为有效的《双人成行》安装目录。
    检查特征文件：ItTakesTwo.exe / ItTakesTwo 可执行文件 或 Content/Paks 目录
    """
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return None

    # 检查特征
    indicators = [
        path / "ItTakesTwo" if SYSTEM != "Windows" else path / "ItTakesTwo.exe",
        path / "ItTakesTwo/Binaries/Win64/ItTakesTwo-Win64-Shipping.exe",
        path / "Content/Paks",
        path / "Engine",
    ]

    for ind in indicators:
        if ind.exists():
            return path.resolve()

    # 深度检查：在子目录中搜索 .pak 文件
    try:
        paks = list(path.rglob("*.pak"))
        if paks:
            return path.resolve()
    except PermissionError:
        pass

    return None


def get_default_output_dir() -> Path:
    """获取默认的解包输出目录"""
    return Path.home() / "it-takes-two-output"
