"""
Debug: Check FBX armature structure and re-export with proper settings
"""
import bpy, os, json

def inspect_and_fix(fbx_path, output_path, arm_name, skel_name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    
    info = {
        "armatures": [],
        "meshes": []
    }
    
    for a in arms:
        bone_names = [b.name for b in a.data.bones]
        root_bones = [b.name for b in a.data.bones if not b.parent]
        info["armatures"].append({
            "name": a.name,
            "data_name": a.data.name if a.data else "NONE",
            "bones": len(bone_names),
            "root_bones": root_bones,
            "first_10_bones": bone_names[:10],
        })
    
    for m in meshes:
        vg_names = [g.name for g in m.vertex_groups]
        parent = m.parent.name if m.parent else "NONE"
        info["meshes"].append({
            "name": m.name,
            "verts": len(m.data.vertices),
            "vgroups": len(vg_names),
            "parent": parent,
            "first_5_vg": vg_names[:5],
        })
    
    print(f"\n=== {fbx_path.split('/')[-1]} ===")
    print(json.dumps(info, indent=2, ensure_ascii=False))
    
    # Fix: rename armature
    for a in arms:
        a.name = arm_name
        a.data.name = skel_name
    
    # Fix: parent meshes to armature
    for m in meshes:
        m.parent = arms[0]
    
    # Make sure the armature modifier is set
    for m in meshes:
        has_arm_mod = False
        for mod in m.modifiers:
            if mod.type == 'ARMATURE':
                mod.object = arms[0]
                has_arm_mod = True
        if not has_arm_mod:
            mod = m.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = arms[0]
    
    # Select all and export
    bpy.ops.object.select_all(action='SELECT')
    
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=True,
        object_types={'MESH', 'ARMATURE'},
        add_leaf_bones=False,
        bake_anim=False,
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE',
        embed_textures=False,
    )
    
    size = os.path.getsize(output_path)
    print(f"\nExported: {output_path} ({size/(1024*1024):.1f} MB)")
    
    return info

inspect_and_fix(
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_retargeted.fbx",
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_v3.fbx",
    "SK_Cody",
    "SK_Cody_Skeleton"
)

inspect_and_fix(
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_nae_retargeted.fbx",
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_v3.fbx",
    "SK_May",
    "SK_May_Skeleton"
)

print("\n✅ All done!")
