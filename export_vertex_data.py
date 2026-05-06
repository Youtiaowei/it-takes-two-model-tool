"""
Blender: Export skinned mesh vertex data from retargeted FBX as raw binary
Output: positions, normals, tangents, UVs, skin weights
"""
import bpy, struct, os, json

def export_vertex_data(fbx_path, output_prefix):
    """Export mesh vertex data from retargeted FBX"""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    if not meshes:
        print(f"No meshes in {fbx_path}")
        return None
    
    result = {
        "file": os.path.basename(fbx_path),
        "meshes": []
    }
    
    for mesh_obj in meshes:
        mesh = mesh_obj.data
        mesh.calc_loop_triangles()
        
        # Get vertex data
        verts = mesh.vertices
        loops = mesh.loops
        uv_layers = mesh.uv_layers
        loop_tris = mesh.loop_triangles
        
        # Ensure we have evaluated the deform modifiers
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = mesh_obj.evaluated_get(depsgraph)
        mesh_eval = obj_eval.to_mesh()
        
        vert_data = {
            "name": mesh_obj.name,
            "vertex_count": len(verts),
            "triangle_count": len(loop_tris),
            "uv_layers": len(uv_layers),
        }
        
        # Collect unique vertices (de-duplicated)
        # For skinned mesh injection, we need per-vertex data
        # Write as binary: for each vertex: pos(12) + normal(4 packed) + tangent(4 packed) + uv(8) + weights(8) + bone_indices(4)
        # UE4 cooked format for skeletal mesh vertices
        # Position: 4 half-floats (X, Y, Z, 1.0) = 8 bytes per vertex
        # Or: 3 floats (12 bytes) depending on optimization
        
        binary_data = bytearray()
        vertex_info = []
        
        for v in verts:
            pos = v.co
            # Normal from vertex (averaged)
            normal = v.normal
            # Get UV from first UV layer
            uv = (0.0, 0.0)
            if uv_layers:
                # Find this vertex in loops to get UV
                for loop in mesh.loops:
                    if loop.vertex_index == v.index:
                        uv = uv_layers[0].data[loop.index].uv
                        break
            
            # Get skin weights from vertex groups
            # The vertex groups are named after game bones (190 groups)
            bone_indices = []
            bone_weights = []
            
            for vg in mesh_obj.vertex_groups:
                try:
                    weight = vg.weight(v.index)
                    if weight > 0.001:
                        bone_indices.append(vg.index)
                        bone_weights.append(weight)
                except:
                    pass
            
            # UE4 uses 4 bones per vertex, normalize
            total_w = sum(bone_weights) or 1.0
            # Pad to 4 bones
            indices = [0] * 4
            weights = [0.0] * 4
            for i, (idx, w) in enumerate(zip(bone_indices[:4], bone_weights[:4])):
                indices[i] = idx
                weights[i] = w / total_w
            
            vertex_info.append({
                "pos": [pos.x, pos.y, pos.z],
                "normal": [normal.x, normal.y, normal.z],
                "uv": [uv.x, uv.y],
                "bone_indices": indices,
                "bone_weights": weights,
            })
            
            # Write binary: position (3 floats = 12 bytes)
            binary_data.extend(struct.pack('<3f', pos.x, pos.y, pos.z))
            # Normal as signed bytes (4 bytes)
            nx = max(-127, min(127, int(normal.x * 127)))
            ny = max(-127, min(127, int(normal.y * 127)))
            nz = max(-127, min(127, int(normal.z * 127)))
            nw = 127  # W component
            binary_data.extend(struct.pack('<4b', nx, ny, nz, nw))
            # Tangent placeholder (4 bytes)
            binary_data.extend(struct.pack('<4b', 127, 0, 0, 127))
            # UV (2 half-floats = 4 bytes)
            import math
            uh = struct.pack('<H', max(0, min(65535, int((uv.x % 1.0) * 65535))))
            vh = struct.pack('<H', max(0, min(65535, int((uv.y % 1.0) * 65535))))
            binary_data.extend(uh + vh)
            # Bone indices (4 bytes)
            binary_data.extend(struct.pack('<4B', *indices))
            # Bone weights (4 bytes as normalized uint8)
            bw_bytes = [max(0, min(255, int(w * 255))) for w in weights]
            binary_data.extend(struct.pack('<4B', *bw_bytes))
        
        # Write binary file
        bin_path = f"{output_prefix}_{mesh_obj.name}.bin"
        with open(bin_path, 'wb') as f:
            f.write(binary_data)
        
        # Write info JSON
        info_path = f"{output_prefix}_{mesh_obj.name}.json"
        with open(info_path, 'w') as f:
            json.dump(vertex_info, f, indent=2)
        
        vert_data["binary_size"] = len(binary_data)
        vert_data["stride"] = len(binary_data) // len(verts) if verts else 0
        vert_data["binary_path"] = bin_path
        result["meshes"].append(vert_data)
        
        print(f"  {mesh_obj.name}: {len(verts)} verts, {len(loop_tris)} tris, stride={vert_data['stride']} bytes")
    
    return result

print("=== Exporting Nekoyama Nae (→ May) ===")
result = export_vertex_data(
    "/home/youtiaowei/it-takes-two-model-tool/models/Nekoyama_nae_retargeted.fbx",
    "/home/youtiaowei/it-takes-two-model-tool/extracted/nekoyama"
)
if result:
    for m in result["meshes"]:
        print(f"  Saved: {m['binary_path']} ({m['binary_size']} bytes)")

print("\n=== Exporting Azusa (→ Cody) ===")
result = export_vertex_data(
    "/home/youtiaowei/it-takes-two-model-tool/models/Azusa_retargeted.fbx",
    "/home/youtiaowei/it-takes-two-model-tool/extracted/azusa"
)
if result:
    for m in result["meshes"]:
        print(f"  Saved: {m['binary_path']} ({m['binary_size']} bytes)")

print("\nDone!")
