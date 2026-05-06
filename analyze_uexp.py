"""
Analyze cooked skeletal mesh .uexp format in detail
Look for vertex buffer patterns
"""
import struct, os

DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"

def analyze_cody_uexp():
    path = os.path.join(DIR, "Cody.uexp")
    with open(path, 'rb') as f:
        data = f.read()
    
    print(f"Cody.uexp: {len(data)} bytes")
    
    # The cooked data starts immediately in .uexp
    # For FSkeletalMesh, the serialization is:
    # FStripDataFlags (4 bytes)
    # Then render data...
    
    # Let's scan for the bulk data headers by looking for patterns
    # FByteBulkData: 4(flags) + 4(count) + 8(size) + 8(offset) = 24 bytes
    
    print(f"\n=== Scanning for potential FByteBulkData headers ===")
    found_bulk = []
    for i in range(0, min(len(data) - 24, 5000), 4):
        bulk_flags = struct.unpack_from('<I', data, i)[0]
        element_count = struct.unpack_from('<I', data, i+4)[0]
        size_on_disk = struct.unpack_from('<Q', data, i+8)[0]
        offset_in_file = struct.unpack_from('<Q', data, i+16)[0]
        
        # Valid bulk data should have reasonable element count and size
        is_reasonable = (
            bulk_flags in (0, 1, 0x41, 0x40) and
            element_count > 100 and element_count < 200000 and
            size_on_disk > 0 and size_on_disk < len(data) and
            (offset_in_file == 0 or (offset_in_file > 0 and offset_in_file < len(data)))
        )
        
        if is_reasonable:
            found_bulk.append((i, bulk_flags, element_count, size_on_disk, offset_in_file))
    
    print(f"Found {len(found_bulk)} potential FByteBulkData headers")
    for offset, flags, count, size, file_off in found_bulk[:10]:
        print(f"  offset={offset}: flags=0x{flags:X} count={count} size_on_disk={size} offset_in_file={file_off}")
    
    # Look for vertex position data (float3 patterns)
    print(f"\n=== Scanning for vertex position data (float3 with reasonable range) ===")
    found_positions = []
    for i in range(0, min(len(data) - 12, 10000), 4):
        x, y, z = struct.unpack_from('<3f', data, i)
        if (-1000 < x < 1000) and (-1000 < y < 1000) and (-1000 < z < 1000):
            # Check repeated pattern (next vertex)
            if i + 24 < len(data):
                x2, y2, z2 = struct.unpack_from('<3f', data, i+12)
                if (-1000 < x2 < 1000) and (-1000 < y2 < 1000) and (-1000 < z2 < 1000):
                    found_positions.append((i, x, y, z, x2, y2, z2))
                    if len(found_positions) >= 20:
                        break
    
    print(f"Found vertex positions at:")
    for offset, x, y, z, x2, y2, z2 in found_positions[:5]:
        print(f"  offset={offset}: ({x:.2f}, {y:.2f}, {z:.2f}) -> ({x2:.2f}, {y2:.2f}, {z2:.2f})")
    
    # Also look at the GLB to find actual vertex positions
    # Then search for those in the uexp
    print(f"\n=== Checking Cody_original.glb vertex data ===")
    glb_path = "/home/youtiaowei/it-takes-two-model-tool/models/Cody_original.glb"
    with open(glb_path, 'rb') as f:
        glb = f.read()
    
    # GLB format: header(12) + JSON chunk + BIN chunk
    # Find BIN chunk
    glb_len = len(glb)
    print(f"GLB size: {glb_len} bytes")
    
    # GLB header: magic(4) + version(4) + length(4)
    magic = struct.unpack_from('<I', glb, 0)[0]
    version = struct.unpack_from('<I', glb, 4)[0]
    glength = struct.unpack_from('<I', glb, 8)[0]
    print(f"GLB: magic=0x{magic:X} version={version} length={glength}")
    
    # First chunk: JSON
    ch_len = struct.unpack_from('<I', glb, 12)[0]
    ch_type = struct.unpack_from('<I', glb, 16)[0]
    print(f"Chunk 1: len={ch_len} type=0x{ch_type:X}")
    json_data = glb[20:20+ch_len]
    print(f"JSON preview: {json_data[:200]}")
    
    # Second chunk: BIN
    ch2_len = struct.unpack_from('<I', glb, 20+ch_len)[0]
    ch2_type = struct.unpack_from('<I', glb, 24+ch_len)[0]
    print(f"Chunk 2: len={ch2_len} type=0x{ch2_type:X}")
    bin_data = glb[28+ch_len:28+ch_len+ch2_len]
    
    # In GLTF, vertex data is in the BIN chunk
    # Look for float3 positions
    print(f"\nGLB BIN vertex samples (first 30 float3):")
    for i in range(30):
        off = i * 12
        if off + 12 <= len(bin_data):
            x, y, z = struct.unpack_from('<3f', bin_data, off)
            if abs(x) < 10000:
                print(f"  [{i}] ({x:.4f}, {y:.4f}, {z:.4f})")

analyze_cody_uexp()
