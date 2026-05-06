"""
Re-export FBX with proper armature names for UE4 import
"""
import bpy, os

def rename_and_export(fbx_path, new_armature_name, output_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    # Rename armature
    arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    if arms:
        arm = arms[0]
        print(f"Renaming armature: {arm.name} -> {new_armature_name}")
        arm.name = new_armature_name
        arm.data.name = new_armature_name + "_Skeleton"
    
    # Select all
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
        path_mode='AUTO',
        embed_textures=False,
    )
    size = os.path.getsize(output_path)
    print(f"Exported: {output_path} ({size/(1024*1024):.1f} MB)")
    print(f"  Armature: {new_armature_name}")

# Re-export Azusa with proper name
rename_and_export(
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_retargeted.fbx",
    "SK_Cody",
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_ue4_ready.fbx"
)

# Re-export Nekoyama with proper name  
rename_and_export(
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_nae_retargeted.fbx",
    "SK_May",
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_ue4_ready.fbx"
)

print("\nDone! Both FBX files re-exported with proper skeleton names.")
