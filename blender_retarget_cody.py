"""
Blender 骨骼重定向 — Azusa → 游戏 Cody (May.ao)
Azusa 是 .blend 文件
"""
import bpy
import os
import sys
import json

GAME_GLB = "/home/youtiaowei/it-takes-two-model-tool/models/Cody_original.glb"
VRC_BLEND = "/home/youtiaowei/it-takes-two-model-tool/models/azusa/source/Azusa.blend"
OUTPUT_FBX = "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_retargeted.fbx"
OUTPUT_BLEND = "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_retargeted.blend"

results = {"steps": [], "errors": []}

def log(msg):
    results["steps"].append(str(msg))
    print(msg)

def deselect():
    bpy.ops.object.select_all(action='DESELECT')

# Step 1
bpy.ops.wm.read_factory_settings(use_empty=True)
log("[1/6] Scene cleared")

# Step 2: Import game GLB
bpy.ops.import_scene.gltf(filepath=GAME_GLB)
log(f"[2/6] Game model loaded: {os.path.basename(GAME_GLB)}")

game_arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
game_arm = game_arms[0]
log(f"  Skeleton: {game_arm.name} ({len(game_arm.data.bones)} bones)")

# Step 3: Remove game meshes
for o in list(bpy.data.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)
log("[3/6] Game meshes removed")

# Step 4: Import Azusa
with bpy.data.libraries.load(VRC_BLEND) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects]
log(f"[4/6] Azusa loaded: {os.path.basename(VRC_BLEND)}")

for obj in data_to.objects:
    if obj is not None:
        bpy.context.collection.objects.link(obj)

vrc_meshes = [o for o in bpy.data.objects if o.type == 'MESH']
vrc_arms = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != game_arm]

log(f"  Azusa meshes: {len(vrc_meshes)}")
for m in vrc_meshes:
    log(f"    {m.name}: {len(m.data.vertices)} verts, {len(m.vertex_groups)} vgroups")

vrc_bones = set()
for arm in vrc_arms:
    for b in arm.data.bones:
        vrc_bones.add(b.name)
    log(f"  Azusa armature: {arm.name} ({len(arm.data.bones)} bones)")

# Step 5: Bind to game skeleton
for arm in vrc_arms:
    bpy.data.objects.remove(arm, do_unlink=True)

for mesh_obj in vrc_meshes:
    mesh_obj.vertex_groups.clear()
    deselect()
    mesh_obj.select_set(True)
    game_arm.select_set(True)
    bpy.context.view_layer.objects.active = game_arm
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        log(f"  ✅ {mesh_obj.name}: bound ({len(mesh_obj.vertex_groups)} vgroups)")
    except Exception as e:
        log(f"  ❌ {mesh_obj.name}: failed - {e}")
        results["errors"].append(str(e))

log("[5/6] ✅ Binding complete")

# Step 6: Export FBX
deselect()
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

bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)

fbx_size = os.path.getsize(OUTPUT_FBX) / (1024*1024)
log(f"[6/6] ✅ Export done!")
log(f"  FBX: {OUTPUT_FBX} ({fbx_size:.1f} MB)")
log(f"  Blend: {OUTPUT_BLEND}")

print(json.dumps(results, indent=2, ensure_ascii=False))
