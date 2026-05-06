"""
v8 - Try entry_offset as absolute PAK file offset 
"""
import struct, os, zlib

PAK_FILE = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak"
OUTPUT_DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"

def read_fstring(data, pos):
    dlen = struct.unpack_from('<i', data, pos)[0]; pos += 4
    if dlen == 0: return '', pos
    abslen = abs(dlen)
    enc = 'utf-16-le' if dlen < 0 else 'utf-8'
    return data[pos:pos+abslen-1].decode(enc, errors='replace'), pos + abslen

fsize = os.path.getsize(PAK_FILE)
with open(PAK_FILE, 'rb') as f:
    f.seek(-204, 2)
    magic, ver, idx_off, idx_sz, _ = struct.unpack('<IIQQ20s', f.read(44))
    print(f"v={ver} idx_off={idx_off} idx_sz={idx_sz}")
    f.seek(idx_off)
    idx_raw = f.read(idx_sz)

# Parse header
pos = 0
mount_point, pos = read_fstring(idx_raw, pos)
file_count = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
print(f"Files: {file_count}")
pos += 8
has_phi = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
phi_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
phi_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8; pos += 20
has_di = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
dir_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
dir_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
print(f"DirIndex: ABSOLUTE offset in file = {dir_off}")
print(f"DirIndex: offset from start of primary index = {dir_off - idx_off}")

# Parse directory index
with open(PAK_FILE, 'rb') as f:
    f.seek(dir_off)
    raw = f.read(dir_sz)
dir_data = zlib.decompress(raw) if raw[0] == 0x78 else raw

dpos = 0
dir_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
for d in range(dir_count):
    dn, dpos = read_fstring(dir_data, dpos)
    ec = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
    for _ in range(ec):
        fn, dpos = read_fstring(dir_data, dpos)
        eo = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        path = (dn.rstrip('/') + '/' + fn).lstrip('/')
        
        if 'Characters' in path and 'May' in path:
            print(f"\n{path}")
            print(f"  entry_offset={eo}")
            
            # Try 1: Absolute offset in PAK file
            if eo + 64 <= fsize:
                with open(PAK_FILE, 'rb') as f:
                    f.seek(eo)
                    data = f.read(64)
                nh = struct.unpack_from('<Q', data, 0)[0]
                fp = struct.unpack_from('<Q', data, 8)[0]
                fs = struct.unpack_from('<Q', data, 16)[0]
                fu = struct.unpack_from('<Q', data, 24)[0]
                print(f"  [absolute pak offset] name_hash={nh:#x} pos={fp} size={fs}/{fu}")
                if 0 < fp < fsize and 0 < fs < 10_000_000:
                    print(f"  ✅ VALID! pos={fp} size={fs}")
            
            # Try 2: Offset within the primary index data (byte 0 of idx_raw)
            if eo + 64 <= len(idx_raw):
                data = idx_raw[eo:eo+64]
                nh = struct.unpack_from('<Q', data, 0)[0]
                fp = struct.unpack_from('<Q', data, 8)[0]
                fs = struct.unpack_from('<Q', data, 16)[0]
                fu = struct.unpack_from('<Q', data, 24)[0]
                print(f"  [idx_raw offset] name_hash={nh:#x} pos={fp} size={fs}/{fu}")
                if 0 < fp < fsize and 0 < fs < 10_000_000:
                    print(f"  ✅ VALID! pos={fp} size={fs}")
            
            # Try 3: Offset from byte 86 (after header)
            off3 = pos + eo
            if off3 + 64 <= len(idx_raw):
                data = idx_raw[off3:off3+64]
                nh = struct.unpack_from('<Q', data, 0)[0]
                fp = struct.unpack_from('<Q', data, 8)[0]
                fs = struct.unpack_from('<Q', data, 16)[0]
                fu = struct.unpack_from('<Q', data, 24)[0]
                print(f"  [idx_raw+header+eo] name_hash={nh:#x} pos={fp} size={fs}/{fu}")
                if 0 < fp < fsize and 0 < fs < 10_000_000:
                    print(f"  ✅ VALID! pos={fp} size={fs}")
            
            # Try 4: XOR decoded (v11 sometimes XORs positions with name hash)
            off4 = pos + eo
            if off4 + 64 <= len(idx_raw):
                data = idx_raw[off4:off4+64]
                nh = struct.unpack_from('<Q', data, 0)[0]
                fp = struct.unpack_from('<Q', data, 8)[0]
                fs = struct.unpack_from('<Q', data, 16)[0]
                # XOR with name hash
                xfp = fp ^ nh
                xfs = fs ^ nh
                print(f"  [XOR decoded] pos={xfp} size={xfs}")
                if 0 < xfp < fsize and 0 < xfs < 10_000_000:
                    print(f"  ✅ VALID! pos={xfp} size={xfs}")
