"""
Try to find the meaty mesh data chunk in the .uexp file
Look for data regions that match the expected vertex buffer size
Cody has 69,924 vertices. Typical strides: 24-48 bytes.
Expected buffer size: 69924 * 32 = 2.24MB to 69924 * 40 = 2.8MB
"""
import struct, os

def analyze_uexp(path, label):
    with open(path, 'rb') as f:
        data = f.read()
    
    print(f"\n=== {label} ({len(data)} bytes, {len(data)/(1024*1024):.1f} MB) ===")
    
    # Scan for large contiguous regions of non-zero data
    # that could be vertex buffers
    chunk_threshold = 500 * 1024  # 500KB minimum for a meaningful vertex buffer
    
    # Check for boundaries: look for areas where data goes from near-zero to non-zero
    zero_runs = []
    non_zero_runs = []
    in_zero = data[0] == 0
    start = 0
    
    for i in range(1, len(data)):
        is_zero = data[i] == 0
        if is_zero != in_zero:
            if in_zero:
                zero_runs.append((start, i - start))
            else:
                non_zero_runs.append((start, i - start))
            start = i
            in_zero = is_zero
    
    if in_zero:
        zero_runs.append((start, len(data) - start))
    else:
        non_zero_runs.append((start, len(data) - start))
    
    # Find large non-zero chunks (potential vertex data)
    large_chunks = [(off, sz) for off, sz in non_zero_runs if sz > chunk_threshold]
    print(f"\nLarge non-zero data chunks (>500KB):")
    for off, sz in sorted(large_chunks):
        mb = sz / (1024*1024)
        pct = off / len(data) * 100
        print(f"  offset={off} ({pct:.1f}% into file) size={sz} bytes ({mb:.1f} MB)")

    # The vertex buffer is likely one of these large chunks
    # Check if any chunk size matches expected vertex count * stride
    expected_verts = 69924 if 'Cody' in label else 62218
    print(f"\nExpected vertices: {expected_verts}")
    for stride in [28, 32, 36, 40, 44, 48]:
        expected_size = expected_verts * stride
        for off, sz in large_chunks:
            if abs(sz - expected_size) < 100:  # close match
                print(f"  stride={stride}: expected_size={expected_size}, found at offset {off}")
    
    # Also look for explicit vertex count as int32
    print(f"\nSearching for vertex count ({expected_verts}) as int32/int16...")
    for i in range(0, len(data)-4):
        val32 = struct.unpack_from('<I', data, i)[0]
        if val32 == expected_verts and i > 100:
            print(f"  Found {expected_verts} as uint32 at offset {i}")
            # Check context
            context = data[max(0,i-8):i+32]
            print(f"    Context: {context.hex()}")
            break
    
    # Also look for the first few positions from the game's GLB as float16
    # Game model positions:
    # V0: (-0.040058, -0.131960, 1.582814)
    # V1: (-0.049266, -0.135032, 1.573012)
    
    # Try searching for half-float packed position (float16^3 = 6 bytes)
    v0_half = struct.pack('<e', -0.040058) + struct.pack('<e', -0.131960) + struct.pack('<e', 1.582814)
    v1_half = struct.pack('<e', -0.049266) + struct.pack('<e', -0.135032) + struct.pack('<e', 1.573012)
    
    pos = 0
    found = []
    while True:
        off = data.find(v0_half, pos)
        if off == -1:
            break
        found.append(off)
        # Check if V1 follows at a regular stride
        for stride in range(24, 60):
            if off + stride + len(v1_half) <= len(data):
                if data[off+stride:off+stride+len(v1_half)] == v1_half:
                    print(f"  Half3 positions found at offset {off}, stride={stride} ✅")
                    break
        pos = off + 1
    
    if not found:
        # Try float16^4 (8 bytes) - common in UE4
        v0_half4 = struct.pack('<e', -0.040058) + struct.pack('<e', -0.131960) + struct.pack('<e', 1.582814) + struct.pack('<e', 1.0)
        v1_half4 = struct.pack('<e', -0.049266) + struct.pack('<e', -0.135032) + struct.pack('<e', 1.573012) + struct.pack('<e', 1.0)
        pos = 0
        while True:
            off = data.find(v0_half4, pos)
            if off == -1:
                break
            for stride in range(24, 60):
                if off + stride + len(v1_half4) <= len(data):
                    if data[off+stride:off+stride+len(v1_half4)] == v1_half4:
                        print(f"  Half4 positions found at offset {off}, stride={stride} ✅")
                        break
            pos = off + 1

analyze_uexp("/home/youtiaowei/it-takes-two-model-tool/extracted/Cody.uexp", "Cody.uexp")
