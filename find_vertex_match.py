"""
Find vertex buffer in .uexp by matching known vertex positions
from the original game GLB model
"""
import bpy, struct, json

# Step 1: Export first vertex position from game GLB as raw bytes
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="/home/youtiaowei/it-takes-two-model-tool/models/Cody_original.glb")

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
if meshes:
    main_mesh = meshes[0]  # First mesh (not Icosphere)
    if main_mesh.name == "Icosphere" and len(meshes) > 1:
        main_mesh = meshes[1]
    
    mesh_data = main_mesh.data
    verts = mesh_data.vertices
    
    print(f"Main mesh: {main_mesh.name}, {len(verts)} vertices")
    
    # Export first 10 vertex positions in various UE4 formats
    positions = []
    for v in list(verts)[:10]:
        positions.append([v.co.x, v.co.y, v.co.z])
    
    with open("/home/youtiaowei/it-takes-two-model-tool/models/cody_first_verts.json", "w") as f:
        json.dump(positions, f)
    
    print("First 10 vertex positions from game model:")
    for i, p in enumerate(positions):
        print(f"  [{i}] ({p[0]:.6f}, {p[1]:.6f}, {p[2]:.6f})")
        # Also show in various encodings
        # 32-bit float (4 bytes each) = 12 bytes
        f32 = struct.pack('<3f', p[0], p[1], p[2])
        print(f"      float32: {f32.hex()}")
        # 16-bit half-float (2 bytes each) = 6 bytes for 3 components
        import math
        def f16(val):
            f = struct.pack('e', float(val))  # Python 3.11+ has 'e' for half
            return f
        # Actually let's use struct for half floats
        try:
            hx = struct.pack('<e', p[0])[0]
            hy = struct.pack('<e', p[1])[0]
            hz = struct.pack('<e', p[2])[0]
            print(f"      half3: {hx:04x}{hy:04x}{hz:04x}")
        except:
            print(f"      (half float not supported in this Python)")
    
    print("\nSearching in Cody.uexp...")
    with open("/home/youtiaowei/it-takes-two-model-tool/extracted/Cody.uexp", 'rb') as f:
        uexp = f.read()
    
    # Search for float32 position bytes
    for v_idx, p in enumerate(positions):
        f32_data = struct.pack('<3f', p[0], p[1], p[2])
        search_pos = 0
        found_at = []
        while True:
            offset = uexp.find(f32_data, search_pos)
            if offset == -1:
                break
            found_at.append(offset)
            search_pos = offset + 1
        if found_at:
            print(f"  Vertex {v_idx} ({p[0]:.4f}, {p[1]:.4f}, {p[2]:.4f}) found at offsets: {found_at[:5]}")
            # Check stride by looking at next vertex position
            for off in found_at[:3]:
                # Try different strides
                for stride in [24, 28, 32, 36, 40, 44]:
                    next_vert_off = off + stride
                    if next_vert_off + 12 <= len(uexp):
                        x2, y2, z2 = struct.unpack_from('<3f', uexp, next_vert_off)
                        # Check if this matches vertex 1
                        if abs(x2 - positions[1][0]) < 0.001 and abs(y2 - positions[1][1]) < 0.001 and abs(z2 - positions[1][2]) < 0.001:
                            print(f"    stride={stride} ✅ - next vertex matches!")
                        # Check if this matches any vertex
                        for vj, pj in enumerate(positions):
                            if vj != v_idx and abs(x2 - pj[0]) < 0.001 and abs(y2 - pj[1]) < 0.001 and abs(z2 - pj[2]) < 0.001:
                                print(f"    stride={stride}: next = vertex {vj}")
                                break
        else:
            print(f"  Vertex {v_idx}: NOT found as float32")
