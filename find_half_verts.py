"""
Search for half-float encoded vertex positions in .uexp
UE4.26 cooked uses FPackedPosition (3x half-float = 6 bytes, or 4x half-float = 8 bytes)
"""
import struct

def hex_to_half(hex_str):
    """Convert hex string to half float"""
    import struct
    # Format: "0021" -> bytes
    b = bytes.fromhex(hex_str)
    return struct.unpack('<e', b)[0]

def read_half3(data, offset):
    """Read 3 half-floats (6 bytes)"""
    hx = struct.unpack_from('<e', data, offset)[0]
    hy = struct.unpack_from('<e', data, offset+2)[0]
    hz = struct.unpack_from('<e', data, offset+4)[0]
    return hx, hy, hz

def read_half4(data, offset):
    """Read 4 half-floats (8 bytes)"""
    hx = struct.unpack_from('<e', data, offset)[0]
    hy = struct.unpack_from('<e', data, offset+2)[0]
    hz = struct.unpack_from('<e', data, offset+4)[0]
    hw = struct.unpack_from('<e', data, offset+6)[0]
    return hx, hy, hz, hw

# First 10 vertex positions from game Cody model (as half3 hex)
half3_vertices = [
    "002100390055",  # V0
    "004e0052004b",  # V1
    "0056008e004d",  # V2
    "0075005f003e",  # V3
    "001600fa003f",  # V4
    "009f00c80034",  # V5
    "0000005c002f",  # V6
    "009e008e0027",  # V7
    "00ec002e0033",  # V8
    "007b001a003c",  # V9
]

# Also try with W=1.0 (half4 = 8 bytes)
half4_vertices = []
for hex_str in half3_vertices:
    h = hex_str + "3c00"  # W=1.0 half-float "3c00"
    half4_vertices.append(h)

print("=== Searching in Cody.uexp ===\n")
with open("/home/youtiaowei/it-takes-two-model-tool/extracted/Cody.uexp", 'rb') as f:
    uexp = f.read()

print("Searching for half3 (6-byte) positions...")
for v_idx, hex_str in enumerate(half3_vertices):
    pattern = bytes.fromhex(hex_str)
    pos = 0
    count = 0
    first_offset = -1
    while True:
        off = uexp.find(pattern, pos)
        if off == -1:
            break
        if first_offset == -1:
            first_offset = off
        count += 1
        pos = off + 1
    if count > 0:
        x, y, z = read_half3(uexp, first_offset)
        print(f"  V{v_idx} (pattern {hex_str}): found {count}x, first at {first_offset} = ({x:.4f}, {y:.4f}, {z:.4f})")

print("\nSearching for half4 (8-byte) positions...")
for v_idx, hex_str in enumerate(half4_vertices):
    pattern = bytes.fromhex(hex_str)
    pos = 0
    count = 0
    first_offset = -1
    while True:
        off = uexp.find(pattern, pos)
        if off == -1:
            break
        if first_offset == -1:
            first_offset = off
        count += 1
        pos = off + 1
    if count > 0:
        x, y, z, w = read_half4(uexp, first_offset)
        print(f"  V{v_idx} (pattern {hex_str}): found {count}x, first at {first_offset} = ({x:.4f}, {y:.4f}, {z:.4f}, {w:.4f})")

# Now check: if V0 at offset X, and stride is S, then V1 should be at X+S
if True:
    print("\n\n=== Checking vertex buffer stride ===")
    # Search for V0 in half4 format
    v0_pattern = bytes.fromhex(half4_vertices[0])
    v1_pattern = bytes.fromhex(half4_vertices[1])
    
    pos = 0
    while True:
        v0_off = uexp.find(v0_pattern, pos)
        if v0_off == -1:
            break
        
        # Compute expected V1 offset for various strides
        for stride in range(28, 65):
            v1_expected = v0_off + stride
            if v1_expected + 8 <= len(uexp):
                # Check if the data at v1_expected matches V1
                v1_data = uexp[v1_expected:v1_expected+8]
                if v1_data == v1_pattern:
                    x0, y0, z0, w0 = read_half4(uexp, v0_off)
                    x1, y1, z1, w1 = read_half4(uexp, v1_expected)
                    print(f"V0 at {v0_off}: stride={stride} ✅")
                    print(f"  V0=({x0:.4f}, {y0:.4f}, {z0:.4f}, {w0:.4f})")
                    print(f"  V1=({x1:.4f}, {y1:.4f}, {z1:.4f}, {w1:.4f})")
                    
                    # Check V2
                    v2_pattern = bytes.fromhex(half4_vertices[2])
                    v2_expected = v0_off + stride * 2
                    if v2_expected + 8 <= len(uexp):
                        v2_data = uexp[v2_expected:v2_expected+8]
                        if v2_data == v2_pattern:
                            print(f"  V2 also matches at stride {stride}!") 
                            # This is our vertex buffer!
                            print(f"\n✅ VERTEX BUFFER FOUND!")
                            print(f"  Start offset: {v0_off}")
                            print(f"  Stride: {stride} bytes")
                            
                            # Count total vertices
                            remaining = len(uexp) - v0_off
                            max_verts = remaining // stride
                            print(f"  Estimated vertices: {max_verts}")
                            
                            # Check end
                            end_marker = v0_off + stride * 69924  # should be 69924 for Cody model
                            print(f"  Expected end: {end_marker} (69924 verts)")
                            if end_marker < len(uexp):
                                print(f"  End byte after mesh: 0x{uexp[end_marker-4:end_marker+4].hex()}")
        pos = v0_off + 1

print("\n\n=== Also checking May.uexp ===")
with open("/home/youtiaowei/it-takes-two-model-tool/extracted/May.uexp", 'rb') as f:
    uexp2 = f.read()

pos = 0
v0_pattern = bytes.fromhex(half4_vertices[0])
v1_pattern = bytes.fromhex(half4_vertices[1])
while True:
    v0_off = uexp2.find(v0_pattern, pos)
    if v0_off == -1:
        break
    for stride in range(28, 65):
        v1_expected = v0_off + stride
        if v1_expected + 8 <= len(uexp2):
            if uexp2[v1_expected:v1_expected+8] == v1_pattern:
                print(f"May: V0 at {v0_off}, stride={stride} ✅")
                break
    pos = v0_off + 1
