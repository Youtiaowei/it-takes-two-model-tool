"""
配置管理模块 — 持久化保存用户设置
"""
import json
import os
from pathlib import Path


CONFIG_DIR = Path.home() / ".it-takes-two-tool"
CONFIG_FILE = CONFIG_DIR / "config.json"
BACKUP_DIR = CONFIG_DIR / "backups"


class Config:
    """应用配置管理"""

    _defaults = {
        "game_path": "",            # 游戏安装目录
        "unrealpak_path": "",       # UnrealPak 工具路径
        "blender_path": "",         # Blender 可执行路径
        "output_dir": "",           # 解包输出目录
        "language": "zh",           # 界面语言
        "theme": "dark",            # 主题
        "last_pak_files": [],       # 最近使用的 .pak 文件列表
        "auto_backup": True,        # 自动备份
    }

    def __init__(self):
        self._data = dict(self._defaults)
        self._load()

    def _load(self):
        """从磁盘加载配置"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._data.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass  # 配置文件损坏时使用默认值

    def save(self):
        """保存配置到磁盘"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    def reset(self):
        """恢复出厂设置"""
        self._data = dict(self._defaults)
        self.save()

    @property
    def game_path(self) -> str:
        return self._data.get("game_path", "")

    @game_path.setter
    def game_path(self, value: str):
        self._data["game_path"] = value
        self.save()

    @property
    def unrealpak_path(self) -> str:
        return self._data.get("unrealpak_path", "")

    @unrealpak_path.setter
    def unrealpak_path(self, value: str):
        self._data["unrealpak_path"] = value
        self.save()

    @property
    def blender_path(self) -> str:
        return self._data.get("blender_path", "")

    @blender_path.setter
    def blender_path(self, value: str):
        self._data["blender_path"] = value
        self.save()

    def __repr__(self):
        return f"Config(game_path={self.game_path!r})"


# 全局单例
config = Config()
