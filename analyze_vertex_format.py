"""
Analyze cooked UE4 skeletal mesh .uexp format
Find vertex buffer and understand the data layout
"""
import struct, os

DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"

def analyze_uexp(path):
    """Analyze cooked skeletal mesh .uexp"""
    with open(path, 'rb') as f:
        data = f.read()
    
    print(f"=== {os.path.basename(path)} ({len(data)} bytes) ===")
    
    # The cooked FSkeletalMesh serialization in UE4.26:
    # The first thing is FStripDataFlags (usually 4-8 bytes)
    
    # Let's scan for the vertex buffer by looking for FBulkData headers
    # FBulkData (cooked): 
    #   int32 BulkDataFlags
    #   int32 ElementCount (vertex count!)
    #   int64 SizeOnDisk
    #   int64 OffsetInFile (0 if inline, offset if in .ubulk)
    
    # The stride (bytes per vertex) = SizeOnDisk / ElementCount
    
    candidates = []
    for i in range(0, min(1000, len(data) - 24)):
        flags = struct.unpack_from('<I', data, i)[0]
        count = struct.unpack_from('<I', data, i+4)[0]
        size_on_disk = struct.unpack_from('<Q', data, i+8)[0]
        offset_in_file = struct.unpack_from('<Q', data, i+16)[0]
        
        # Valid vertex count (100-200k), valid size, inline data (offset=0 or offset in range)
        if (100 < count < 200000 and 
            size_on_disk > 0 and size_on_disk < len(data) and
            (offset_in_file == 0 or (0 < offset_in_file < len(data)))):
            
            stride = size_on_disk / count
            if stride.is_integer() and 20 <= int(stride) <= 48:
                candidates.append((i, flags, count, int(stride), offset_in_file))
    
    if candidates:
        print(f"Found {len(candidates)} potential vertex buffers:")
        for offset, flags, count, stride, file_off in candidates[:10]:
            loc = "inline at " + str(file_off) if file_off > 0 else "inline"
            print(f"  offset={offset} flags=0x{flags:X} verts={count} stride={stride}B {loc}")
        
        # If we find the vertex buffer, analyze the data format
        best = candidates[0]
        offset = best[0]
        if best[4] > 0:
            data_start = best[4]
        else:
            data_start = offset + 24  # right after FBulkData header
        
        stride = best[3]
        count = best[1]
        print(f"\nAnalyzing vertex buffer at {data_start}, stride={stride}B, count={count}")
        
        # Dump first 3 vertices as raw bytes
        for v in range(min(3, count)):
            start = data_start + v * stride
            if start + stride <= len(data):
                print(f"\n  Vertex {v}: (hex)")
                for b in range(0, stride, 4):
                    val32 = struct.unpack_from('<I', data, start+b)[0]
                    valf = struct.unpack_from('<f', data, start+b)[0]
                    print(f"    +{b:3d}: 0x{val32:08x} = {valf:.6f}")
        
        # Try to interpret as standard UE4 vertex format:
        # For skeletal meshes, common formats:
        # Position(12B float3) + Normal(4B packed) + Tangent(4B packed) + UV(8B float2) + Weights(8B) = 36B
        # Position(8B half4) + Normal(4B) + Tangent(4B) + UV(4B half2) + Color(4B) + Weights(8B) = 32B
        
        if stride == 32:
            print(f"\n  Likely format (32B): Position(half4=8) + TangentX(4) + TangentZ(4) + UV(half2=4) + Color(4) + Weights(8)")
        elif stride == 36:
            print(f"\n  Likely format (36B): Position(float3=12) + Normal(4) + Tangent(4) + UV(float2=8) + Weights(8)")
        elif stride == 40:
            print(f"\n  Likely format (40B): Position(float3=12) + Normal(4) + Tangent(4) + UV(half2=4) + Color(4) + Weights(8) + ???(4)")
        elif stride == 28:
            print(f"\n  Likely format (28B): Position(float3=12) + Normal(4) + Tangent(4) + UV(half2=4) + Weights(4)")

    # No candidates found, do a deeper analysis
    if not candidates:
        print("No vertex buffer found with expected pattern")
        print("Analyzing first 128 bytes:")
        for i in range(0, 128, 16):
            vals = struct.unpack_from('<4I', data, i)
            floats = struct.unpack_from('<4f', data, i)
            print(f"  {i:3d}: 0x{vals[0]:08x} 0x{vals[1]:08x} 0x{vals[2]:08x} 0x{vals[3]:08x} = {floats[0]:.4f} {floats[1]:.4f} {floats[2]:.4f} {floats[3]:.4f}")
        
        # Search for the known vertex positions from our FBX
        # The GLB vertex 0 position was something like...
        print("\nSearching for vertex position patterns...")
        # Look for small positive float values
        for i in range(0, min(5000, len(data)-12), 4):
            x, y, z = struct.unpack_from('<3f', data, i)
            if abs(x) < 200 and abs(y) < 200 and abs(z) < 200:
                # Next 12 bytes could be next vertex
                if i + 24 < len(data):
                    x2, y2, z2 = struct.unpack_from('<3f', data, i+12)
                    x3, y3, z3 = struct.unpack_from('<3f', data, i+24)
                    if abs(x2) < 200 and abs(y2) < 200 and abs(z2) < 200:
                        print(f"  Found vertex sequence at offset {i}:")
                        print(f"    v0: ({x:.4f}, {y:.4f}, {z:.4f})")
                        print(f"    v1: ({x2:.4f}, {y2:.4f}, {z2:.4f})")
                        print(f"    stride guesses: {i+24-(i+12)} (12 B stride) or calc from next vert")
                        # Check stride by finding v3
                        for stride_guess in [12, 16, 20, 24, 28, 32, 36, 40]:
                            next_v = i + stride_guess * 3
                            if next_v + 12 < len(data):
                                x4, y4, z4 = struct.unpack_from('<3f', data, next_v)
                                if abs(x4) < 200:
                                    print(f"    stride={stride_guess}: v3 at {next_v}=({x4:.4f}, {y4:.4f}, {z4:.4f})")
                        break

for file in ['Cody.uexp', 'May.uexp']:
    analyze_uexp(os.path.join(DIR, file))
    print()
