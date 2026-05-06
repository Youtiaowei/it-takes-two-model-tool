"""Analyze UE4 cooked skeletal mesh .uasset/.uexp structure"""
import struct, os

DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"

def analyze_uasset(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    print(f"=== {os.path.basename(path)} ({len(data)} bytes) ===")
    
    pos = 0
    tag = struct.unpack_from('<I', data, pos)[0]; pos += 4
    print(f"Package Tag: 0x{tag:08X}")
    
    legacy_ver = struct.unpack_from('<I', data, pos)[0]; pos += 4
    engine_ver = struct.unpack_from('<I', data, pos)[0]; pos += 4
    custom_ver_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
    pos += custom_ver_count * 8  # skip custom versions
    
    total_header_size = struct.unpack_from('<I', data, pos)[0]; pos += 4
    pkg_name_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
    pkg_name = data[pos:pos+pkg_name_len].decode('utf-8', errors='replace')
    pos += pkg_name_len
    
    flags = struct.unpack_from('<I', data, pos)[0]; pos += 4
    print(f"Package Name: {pkg_name}")
    print(f"Package Flags: 0x{flags:08X} (cooked={bool(flags & 1)})")
    
    name_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
    name_offset = struct.unpack_from('<I', data, pos)[0]; pos += 4
    print(f"Names: {name_count} at offset {name_offset}")
    
    export_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
    export_offset = struct.unpack_from('<I', data, pos)[0]; pos += 4
    print(f"Exports: {export_count} at offset {export_offset}")
    
    import_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
    import_offset = struct.unpack_from('<I', data, pos)[0]; pos += 4
    print(f"Imports: {import_count} at offset {import_offset}")
    
    # Read imports (dependencies)
    print(f"\n--- Imports (first 20) ---")
    temp_pos = import_offset
    for i in range(min(import_count, 20)):
        class_package = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        class_name = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        outer_import = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        obj_name = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        print(f"  [{i}] class_pkg={class_package} class={class_name} outer={outer_import} obj={obj_name}")

    # Read exports
    print(f"\n--- Exports ---")
    temp_pos = export_offset
    for i in range(export_count):
        class_index = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        super_index = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        outer_index = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        obj_name = struct.unpack_from('<I', data, temp_pos)[0]; temp_pos += 4
        serial_offset = struct.unpack_from('<Q', data, temp_pos)[0]; temp_pos += 8
        serial_size = struct.unpack_from('<Q', data, temp_pos)[0]; temp_pos += 8
        print(f"  [{i}] class={class_index} name={obj_name} offset={serial_offset} size={serial_size}")

for file in ['Cody.uasset', 'May.uasset']:
    analyze_uasset(os.path.join(DIR, file))
    print()

# Also check uexp structure
def analyze_uexp(path):
    with open(path, 'rb') as f:
        data = f.read()
    print(f"=== {os.path.basename(path)} ({len(data)} bytes) ===")
    
    # Cooked UE4 skeletal mesh format:
    # Serialized data starts at the beginning of .uexp
    # For skeletal mesh, the serialized data is:
    #   FByteBulkData (vertex buffer)
    #   FByteBulkData (index buffer) 
    #   FSkinWeightVertexBuffer
    #   etc.
    
    # Let's look at the first 64 bytes to understand the format
    print("First 64 bytes (hex):")
    for i in range(0, 64, 8):
        val = struct.unpack_from('<Q', data, i)[0]
        print(f"  offset {i:4d}: 0x{val:016x} ({val})")
    
    # Check for common patterns
    # UE4 skeletal mesh cooked data starts with:
    # The serialized FStripDataFlags (4 bytes)
    # Then the vertex buffer as FByteBulkData
    # FByteBulkData: BulkDataFlags(4) + ElementCount(4) + SizeOnDisk(8) + OffsetInFile(8)
    
    pos = 0
    strip_flags = struct.unpack_from('<I', data, pos)[0]; pos += 4
    print(f"\nPossible strip flags: 0x{strip_flags:08X}")
    
    # FByteBulkData for vertex buffer
    bulk_flags = struct.unpack_from('<I', data, pos)[0]; pos += 4
    element_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
    size_on_disk = struct.unpack_from('<Q', data, pos)[0]; pos += 8
    offset_in_file = struct.unpack_from('<Q', data, pos)[0]; pos += 8
    print(f"BulkData: flags=0x{bulk_flags:08X} elements={element_count} size_on_disk={size_on_disk} offset_in_file={offset_in_file}")

    # If offset_in_file > 0, it's stored in a .ubulk. Otherwise it's inline.
    if offset_in_file > 0 and offset_in_file < len(data):
        vert_data = data[offset_in_file:offset_in_file+128]
        print(f"  First 128 bytes at offset {offset_in_file}:")
        for i in range(0, min(128, size_on_disk or element_count*4), 16):
            vals = struct.unpack_from('<4f' if i+16 <= min(128, size_on_disk or element_count*4) else '4H', data, offset_in_file+i)
            print(f"    {i:4d}: {vals}")
    else:
        # Data is inline after the bulk data header
        inline_data_start = pos
        print(f"  Data inline at offset {inline_data_start}")
        # Read first few vertices (assuming float3 position)
        for i in range(3):  # read 3 vertices
            v_pos = inline_data_start + i * 12
            if v_pos + 12 <= len(data):
                x, y, z = struct.unpack_from('<3f', data, v_pos)
                print(f"  Vertex {i}: ({x:.4f}, {y:.4f}, {z:.4f})")

for file in ['Cody.uexp', 'May.uexp']:
    analyze_uexp(os.path.join(DIR, file))
    print()
