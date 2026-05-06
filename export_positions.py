"""
Export vertex positions from retargeted FBX for pattern matching
"""
import bpy, struct, json

def export_first_verts(fbx_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    all_vertices = []
    
    for m in meshes:
        print(f"Mesh: {m.name} ({len(m.data.vertices)} verts)")
        # Get first 100 vertices as float3
        for v in list(m.data.vertices)[:100]:
            all_vertices.extend([v.co.x, v.co.y, v.co.z])
        
        # Also export as binary
        bin_data = bytearray()
        for v in m.data.vertices:
            bin_data.extend(struct.pack('<3f', v.co.x, v.co.y, v.co.z))
        
        bin_path = fbx_path.replace('.fbx', f'_{m.name}_pos.bin')
        with open(bin_path, 'wb') as f:
            f.write(bin_data)
        print(f"  Exported positions to: {bin_path}")
    
    return all_vertices

print("=== Nekoyama Nae positions ===")
nek_pos = export_first_verts(
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_nae_retargeted.fbx"
)

print("\n=== Azusa positions ===")
azu_pos = export_first_verts(
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_retargeted.fbx"
)

print("\nFirst 10 positions (Nekoyama):")
for i in range(0, min(30, len(nek_pos)), 3):
    print(f"  ({nek_pos[i]:.4f}, {nek_pos[i+1]:.4f}, {nek_pos[i+2]:.4f})")
