"""Analyze VRChat model skeleton using Blender Python"""
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import Azusa blend file
azusa_path = '/home/youtiaowei/it-takes-two-model-tool/models/azusa/source/Azusa.blend'

# Append the armature and mesh from the blend file
with bpy.data.libraries.load(azusa_path) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects]

# Link all loaded objects to the scene
for obj in data_to.objects:
    if obj is not None:
        bpy.context.collection.objects.link(obj)

# Find armature
armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
print(f"\n=== Azusa (VRChat) ===")
print(f"Found {len(armatures)} armatures")

for arm in armatures:
    print(f"\nArmature: {arm.name}")
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    
    bones = arm.data.edit_bones
    print(f"Total bones: {len(bones)}")
    
    # Print bone hierarchy (first 40 bones)
    root_bones = [b for b in bones if b.parent is None]
    print(f"Root bones: {[b.name for b in root_bones]}")
    
    def print_bone_tree(bone, indent=0):
        if indent > 30:  # Limit depth
            return
        print(f"{'  ' * indent}{bone.name}")
        for child in bone.children:
            print_bone_tree(child, indent + 1)
    
    for root in root_bones:
        print_bone_tree(root)
    
    bpy.ops.object.mode_set(mode='OBJECT')

# Clean up
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
