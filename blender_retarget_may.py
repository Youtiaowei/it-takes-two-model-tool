"""
Blender 骨骼重定向脚本 — Nekoyama Nae → 游戏 May (Cody.ao)
"""
import bpy
import os
import sys
import json

GAME_GLB = "/home/youtiaowei/it-takes-two-model-tool/models/May_original.glb"
VRC_FBX = "/home/youtiaowei/it-takes-two-model-tool/models/nekoyama/source/Nekoyama_nae.fbx"
OUTPUT_FBX = "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_nae_retargeted.fbx"
OUTPUT_BLEND = "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_nae_retargeted.blend"

results = {"steps": [], "errors": []}

def log(msg):
    results["steps"].append(str(msg))
    print(msg)

def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')

# ========== 第1步 ==========
bpy.ops.wm.read_factory_settings(use_empty=True)
log("[1/6] ✅ 场景清空")

# ========== 第2步：导入游戏 GLB ==========
bpy.ops.import_scene.gltf(filepath=GAME_GLB)
log(f"[2/6] ✅ 导入游戏模型: {os.path.basename(GAME_GLB)}")

game_arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
if not game_arms:
    log("❌ 未找到游戏骨架！")
    print(json.dumps(results)); sys.exit(1)

game_arm = game_arms[0]
log(f"  骨架: {game_arm.name} ({len(game_arm.data.bones)} bones)")

# ========== 第3步：删除游戏网格 ==========
for o in list(bpy.data.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)
log("[3/6] ✅ 删除了游戏网格，保留骨架")

# ========== 第4步：导入 VRChat 模型 ==========
bpy.ops.import_scene.fbx(filepath=VRC_FBX)
log(f"[4/6] ✅ 导入 VRChat 模型: {os.path.basename(VRC_FBX)}")

vrc_meshes = [o for o in bpy.data.objects if o.type == 'MESH']
vrc_arms = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != game_arm]

log(f"  VRChat 网格: {len(vrc_meshes)} 个")
for m in vrc_meshes:
    log(f"    {m.name}: {len(m.data.vertices)} 顶点, {len(m.vertex_groups)} 权重组")

# VRChat 骨架骨骼名
vrc_bones = set()
for arm in vrc_arms:
    for b in arm.data.bones:
        vrc_bones.add(b.name)
    log(f"  VRChat 骨架: {arm.name} ({len(arm.data.bones)} bones)")

# ========== 第5步：清理并绑定 ==========
# 先删除 VRChat 骨架
for arm in vrc_arms:
    bpy.data.objects.remove(arm, do_unlink=True)

# 清理旧权重组并绑定到游戏骨架
for mesh_obj in vrc_meshes:
    # 清除所有指向 VRChat 骨骼的权重组
    for vg_name in list(mesh_obj.vertex_groups.keys()):
        if vg_name in vrc_bones:
            mesh_obj.vertex_groups.remove(mesh_obj.vertex_groups[vg_name])
    
    # 清除剩余的权重组（全部清掉，让自动权重重新生成）
    mesh_obj.vertex_groups.clear()
    
    # 绑定到游戏骨架
    deselect_all()
    mesh_obj.select_set(True)
    game_arm.select_set(True)
    bpy.context.view_layer.objects.active = game_arm
    
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        vg_count = len(mesh_obj.vertex_groups)
        log(f"  ✅ {mesh_obj.name}: 绑定成功 ({vg_count} 权重组)")
    except Exception as e:
        log(f"  ❌ {mesh_obj.name}: 绑定失败 - {e}")
        results["errors"].append(str(e))

log("[5/6] ✅ 骨骼绑定完成")

# ========== 第6步：导出 FBX ==========
deselect_all()
game_arm.select_set(True)
for m in vrc_meshes:
    m.select_set(True)

bpy.ops.export_scene.fbx(
    filepath=OUTPUT_FBX,
    use_selection=True,
    object_types={'MESH', 'ARMATURE'},
    add_leaf_bones=False,
    bake_anim=False,
    axis_forward='-Z',
    axis_up='Y',
    mesh_smooth_type='FACE',
    path_mode='AUTO',
    embed_textures=False,
)

# 保存 .blend
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)

log(f"[6/6] ✅ 导出完成!")
log(f"  FBX: {OUTPUT_FBX}")
log(f"  Blend: {OUTPUT_BLEND}")

# 验证
import os as _os
fbx_size = _os.path.getsize(OUTPUT_FBX) / (1024*1024)
log(f"  文件大小: {fbx_size:.1f} MB")

print(json.dumps(results, indent=2, ensure_ascii=False))
