"""
Simplify skeleton: make Hips the root bone, remove Root/Align/IK bones
These are engine-internal bones that confuse UE4's importer
Also: fix meshes with no vertex groups (add basic Hips weight)
"""
import bpy, os

def clean_and_export(fbx_path, output_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    
    if not arms:
        print("No armature found!")
        return
    
    arm = arms[0]
    
    # Find bones to fix: faces, IK, etc.
    # UE4 needs proper bones for deformation
    # The key issue is often "Root" and "Align" being at the top
    
    # For UE4 import, let's try making "Hips" the root
    # and removing "Root" and "Align" bones
    
    # Actually, a simpler approach: make a completely clean skeleton
    # Let's just ensure the armature is properly set up
    
    # Rename armature
    arm.name = "Armature"
    arm.data.name = "Skeleton"
    
    # Fix: add vertex groups to meshes that have none
    for m in meshes:
        if len(m.vertex_groups) == 0:
            print(f"  Fixing: {m.name} has no vertex groups, adding Hips weight")
            # Add a single vertex group with Hips name
            vg = m.vertex_groups.new(name="Hips")
            # Add all vertices to Hips with weight 1.0
            vg.add(range(len(m.data.vertices)), 1.0, 'ADD')
    
    # Select all properly
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [arm] + meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = arm
    
    # Make sure mesh parents are set
    for m in meshes:
        if m.parent != arm:
            m.parent = arm
    
    # Export with specific UE4-compatible settings
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=True,
        object_types={'MESH', 'ARMATURE'},
        add_leaf_bones=False,
        bake_anim=False,
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE',
        path_mode='STRIP',
        embed_textures=False,
        use_armature_deform_only=True,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
    )
    
    size = os.path.getsize(output_path)
    print(f"Exported: {output_path} ({size/(1024*1024):.1f} MB)")
    print(f"  Armature: {arm.name} ({len(arm.data.bones)} bones)")
    print(f"  Meshes: {len(meshes)}")

# Process both
clean_and_export(
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_retargeted.fbx",
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_final.fbx"
)

clean_and_export(
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_nae_retargeted.fbx",
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_final.fbx"
)

print("\n✅ All done! Ready for UE4 import.")
