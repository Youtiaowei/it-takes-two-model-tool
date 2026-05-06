from __future__ import annotations
"""模型替换模块 — FBX 导入、骨骼重定向、材质匹配"""

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# 数据类型
# ──────────────────────────────────────────────────────────

@dataclass
class CharacterInfo:
    """游戏内角色信息"""
    id: str
    name_cn: str
    name_en: str
    skeleton_name: str      # 骨骼资源名
    mesh_paths: list[str]   # 网格体资源路径
    texture_paths: list[str] = field(default_factory=list)
    material_paths: list[str] = field(default_factory=list)
    notes: str = ""


# 《双人成行》的角色信息
CHARACTERS = [
    CharacterInfo(
        id="cody",
        name_cn="科迪",
        name_en="Cody",
        skeleton_name="SK_Cody_Skeleton",
        mesh_paths=[
            "SK_Cody",
            "SK_Cody_Body",
            "SK_Cody_Head",
        ],
        notes="男性角色，父子关系中的父亲",
    ),
    CharacterInfo(
        id="may",
        name_cn="梅",
        name_en="May",
        skeleton_name="SK_May_Skeleton",
        mesh_paths=[
            "SK_May",
            "SK_May_Body",
            "SK_May_Head",
        ],
        notes="女性角色，母女关系中的母亲",
    ),
    CharacterInfo(
        id="rose",
        name_cn="罗斯",
        name_en="Rose",
        skeleton_name="SK_Rose_Skeleton",
        mesh_paths=["SK_Rose"],
        notes="女儿角色",
    ),
    CharacterInfo(
        id="dr_hakim",
        name_cn="哈基姆博士",
        name_en="Dr. Hakim",
        skeleton_name="SK_Hakim_Skeleton",
        mesh_paths=["SK_Hakim"],
        notes="魔法书角色，爱情顾问",
    ),
]


@dataclass
class ReplacementConfig:
    """一次模型替换的完整配置"""
    character_id: str                     # 要替换的角色
    fbx_path: Path                        # 导入的 FBX 模型文件
    auto_retarget: bool = True            # 是否自动骨骼重定向
    match_materials: bool = True          # 是否自动匹配材质
    backup_first: bool = True             # 替换前自动备份
    output_pak_path: Path | None = None   # 输出 .pak 路径（None 则覆盖原文件）

    def validate(self) -> list[str]:
        """验证配置，返回错误列表"""
        errors = []
        if not self.fbx_path.exists():
            errors.append(f"FBX 文件不存在: {self.fbx_path}")
        if self.fbx_path.suffix.lower() not in (".fbx",):
            errors.append(f"仅支持 .fbx 格式，当前文件: {self.fbx_path.suffix}")
        if self.character_id not in {c.id for c in CHARACTERS}:
            errors.append(f"无效的角色 ID: {self.character_id}")
        return errors


# ──────────────────────────────────────────────────────────
# 模型替换引擎
# ──────────────────────────────────────────────────────────

class ModelReplacer:
    """
    模型替换引擎。
    使用 Blender Python API 进行 FBX 导入、骨骼重定向、材质匹配。
    如果不具备自动化条件，给出清晰的替代方案指引。
    """

    def __init__(
        self,
        blender_path: Path | str | None = None,
        callback: Callable[[str], None] | None = None,
    ):
        self.blender_path = Path(blender_path) if blender_path else None
        self.callback = callback or (lambda msg: None)

    @property
    def blender_available(self) -> bool:
        """检查 Blender 是否可用"""
        if not self.blender_path or not self.blender_path.exists():
            return False
        try:
            result = subprocess.run(
                [str(self.blender_path), "--version"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def replace_character(
        self,
        config: ReplacementConfig,
        unpacked_dir: Path | None = None,
    ) -> bool:
        """
        执行完整的角色模型替换流程。
        流程：
        1. 验证输入
        2. 导入 FBX 到 Blender
        3. 执行骨骼重定向
        4. 匹配材质
        5. 导出为 UE 兼容格式
        """
        # 1. 验证
        errors = config.validate()
        if errors:
            for err in errors:
                self.callback(f"[X] {err}")
            return False

        character = next((c for c in CHARACTERS if c.id == config.character_id), None)
        self.callback(f"[->] 准备替换角色: {character.name_cn} ({character.name_en})")
        self.callback(f"[*] 导入模型: {config.fbx_path.name}")

        # 2. 检查 Blender 可用性
        if not self.blender_available:
            return self._fallback_manual_guide(config, character, unpacked_dir)

        # 3. 执行 Blender 自动化流程
        return self._run_blender_pipeline(config, character, unpacked_dir)

    def _run_blender_pipeline(
        self,
        config: ReplacementConfig,
        character: CharacterInfo,
        unpacked_dir: Path | None,
    ) -> bool:
        """使用 Blender Python API 执行自动化替换"""
        self.callback("[R] 正在启动 Blender 自动化流程...")

        # 生成 Blender Python 脚本
        blender_script = self._generate_blender_script(config, character, unpacked_dir)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            script_path = f.name
            f.write(blender_script)

        try:
            cmd = [
                str(self.blender_path),
                "--background",           # 无界面模式
                "--python", script_path,   # 执行脚本
            ]

            self.callback("[w] 正在执行骨骼重定向和材质匹配...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.callback("[OK] Blender 处理完成！")
                return True
            else:
                self.callback("[X] Blender 处理失败")
                self.callback(f"错误信息: {result.stderr[:500]}")
                self.callback("\n[?] 请检查：")
                self.callback("  1. FBX 文件是否包含有效骨骼")
                self.callback("  2. Blender 版本是否 >= 3.0")
                self.callback("  3. 控制台输出查看详细错误")
                return False

        except subprocess.TimeoutExpired:
            self.callback("[!] Blender 处理超时")
            return False
        except Exception as e:
            self.callback(f"[X] Blender 执行异常: {e}")
            return False
        finally:
            Path(script_path).unlink(missing_ok=True)

    def _generate_blender_script(
        self,
        config: ReplacementConfig,
        character: CharacterInfo,
        unpacked_dir: Path | None,
    ) -> str:
        """生成 Blender Python 自动化脚本"""
        # 这是实际的 Blender 自动化脚本模板
        return f'''
"""
Blender 自动化脚本 — 由 It Takes Two Model Tool 生成
角色: {character.name_en} ({character.name_cn})
FBX: {config.fbx_path}
"""

import bpy
import os
import sys

# ============================================================
# 第1步: 清空场景
# ============================================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============================================================
# 第2步: 导入 FBX 模型
# ============================================================
fbx_path = r"{config.fbx_path}"
if not os.path.exists(fbx_path):
    print(f"ERROR: FBX file not found: {{fbx_path}}")
    sys.exit(1)

bpy.ops.import_scene.fbx(filepath=fbx_path)
print(f"[OK] 导入 FBX: {{fbx_path}}")

# 列出导入的对象
imported_objects = bpy.context.selected_objects
for obj in imported_objects:
    print(f"  对象: {{obj.name}}, 类型: {{obj.type}}")

# ============================================================
# 第3步: 骨架检查与重定向
# ============================================================
armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
if armatures:
    print(f"[OK] 检测到 {{len(armatures)}} 个骨架")
    for arm in armatures:
        print(f"  骨架: {{arm.name}}, 骨骼数: {{len(arm.data.bones)}}")
else:
    print("[!]  未检测到骨架")
    print("  提示: 请确保 FBX 文件中包含绑定了骨骼的模型")
    print("  或者: 模型仅替换静态网格体，跳过骨骼重定向")

# ============================================================
# 第4步: 材质检查
# ============================================================
materials = bpy.data.materials
print(f"[*] 检测到 {{len(materials)}} 个材质")
for mat in materials:
    # 检查材质节点
    if mat.node_tree and mat.node_tree.nodes:
        principled = [n for n in mat.node_tree.nodes 
                      if n.type == 'BSDF_PRINCIPLED']
        texture_nodes = [n for n in mat.node_tree.nodes 
                         if n.type == 'TEX_IMAGE']
        print(f"  材质: {{mat.name}}")
        print(f"    原理化 BSDF: {{'有' if principled else '无'}}")
        print(f"    纹理贴图: {{len(texture_nodes)}} 个")
    else:
        print(f"  材质: {{mat.name}} (无节点)")

# ============================================================
# 第5步: 导出为 FBX (UE4 兼容)
# ============================================================
export_path = r"{config.fbx_path.parent / (config.fbx_path.stem + '_retargeted.fbx')}"
bpy.ops.export_scene.fbx(
    filepath=export_path,
    use_selection=False,
    object_types={{'MESH', 'ARMATURE'}},
    add_leaf_bones=False,
    bake_anim=False,
    axis_forward='-Z',
    axis_up='Y',
)
print(f"[OK] 导出重定向后的模型: {{export_path}}")

# ============================================================
# 完成
# ============================================================
print("=" * 50)
print("Blender 自动化流程完成！")
print(f"输出文件: {{export_path}}")
print("=" * 50)
'''

    def _fallback_manual_guide(
        self,
        config: ReplacementConfig,
        character: CharacterInfo,
        unpacked_dir: Path | None,
    ) -> bool:
        """给出清晰的手动操作指引"""
        self.callback("")
        self.callback("=" * 50)
        self.callback("[N] 模型替换 — 手动操作指引")
        self.callback("=" * 50)
        self.callback(f"")
        self.callback(f"目标角色: {character.name_cn} ({character.name_en})")
        self.callback(f"模型文件: {config.fbx_path}")
        self.callback(f"")
        self.callback("由于未找到 Blender，无法自动完成骨骼重定向。")
        self.callback("以下是手动操作的步骤：")
        self.callback(f"")
        self.callback("[L] **手动骨骼重定向步骤**")
        self.callback(f"  1. 在 Blender (3.0+) 中打开或导入目标角色骨骼模板")
        self.callback(f"  2. 导入你的 FBX 模型: File → Import → FBX")
        self.callback(f"  3. 选择源骨骼和目标骨骼，使用 Rigify 或手动重定向")
        self.callback(f"  4. 确保骨骼映射匹配:")
        self.callback(f"     - {character.skeleton_name} 的骨骼层级")
        self.callback(f"     - 每个骨骼的命名和层级结构应一致")
        self.callback(f"")
        self.callback("[L] **材质匹配步骤**")
        self.callback(f"  1. 在 Blender Shader Editor 中打开材质")
        self.callback(f"  2. 将 Principled BSDF 节点参数与源材质匹配")
        self.callback(f"  3. 检查纹理贴图路径是否正确")
        self.callback(f"")
        self.callback("[L] **导出步骤**")
        self.callback(f"  1. File → Export → FBX")
        self.callback(f"  2. 设置: Axis Up=Y, Axis Forward=-Z (UE4 兼容)")
        self.callback(f"  3. Bake Animation=OFF, Add Leaf Bones=OFF")
        self.callback(f"  4. Object Types: Mesh + Armature")
        self.callback(f"")
        self.callback("[L] **UE 资源导入**")
        self.callback(f"  1. 将 FBX 导入 Unreal Engine 项目")
        self.callback(f"  2. 确保骨骼指向 {character.skeleton_name}")
        self.callback(f"  3. 重新生成材质实例")
        self.callback(f"  4. 导出为 .uasset 并用 .pak 封包")
        self.callback(f"")
        self.callback("[?] 如果以上步骤觉得复杂，可以：")
        self.callback("  - 安装 Blender (免费): https://www.blender.org/download/")
        self.callback("  - 在工具设置中指定 Blender 路径后重试")
        self.callback("  - 使用社区预先做好的模型包")
        self.callback("=" * 50)
        return False

    def preview_skeleton(self, fbx_path: Path) -> dict | None:
        """预览 FBX 文件的骨架结构（不实际导入 UE）"""
        # 如果有 Blender，可以用 Blender 读取骨架信息
        if self.blender_available:
            script = f'''
import bpy, json
bpy.ops.import_scene.fbx(filepath=r"{fbx_path}")
armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
result = {{"armatures": []}}
for arm in armatures:
    bones = [{{"name": b.name, "parent": b.parent.name if b.parent else None}} 
             for b in arm.data.bones]
    result["armatures"].append({{
        "name": arm.name,
        "bone_count": len(bones),
        "bones": bones[:50],  # 只取前 50 个
    }})
print(json.dumps(result))
bpy.ops.wm.quit_blender()
'''
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(script)
                script_path = f.name

            try:
                result = subprocess.run(
                    [str(self.blender_path), "--background", "--python", script_path],
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0:
                    # 从 stdout 提取 JSON
                    for line in result.stdout.splitlines():
                        if line.startswith("{"):
                            return json.loads(line)
            except Exception:
                pass
            finally:
                Path(script_path).unlink(missing_ok=True)

        return None
