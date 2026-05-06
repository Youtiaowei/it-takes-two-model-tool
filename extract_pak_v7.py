"""
v7 - try EntryOffset as absolute offset in primary index
"""
import struct, os, zlib

PAK_FILE = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak"
OUTPUT_DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"
TARGET_FILES = [
    "Nuts/Content/Characters/Cody/Cody.uasset",
    "Nuts/Content/Characters/Cody/Cody.uexp",
    "Nuts/Content/Characters/May/May.uasset",
    "Nuts/Content/Characters/May/May.uexp",
]

def read_fstring(data, pos):
    dlen = struct.unpack_from('<i', data, pos)[0]; pos += 4
    if dlen == 0: return '', pos
    abslen = abs(dlen)
    enc = 'utf-16-le' if dlen < 0 else 'utf-8'
    return data[pos:pos+abslen-1].decode(enc, errors='replace'), pos + abslen

fsize = os.path.getsize(PAK_FILE)
with open(PAK_FILE, 'rb') as f:
    f.seek(-204, 2)
    footer = f.read(44)
    magic, ver, idx_off, idx_sz, _ = struct.unpack('<IIQQ20s', footer)
    print(f"Index at {idx_off}, size {idx_sz}")
    f.seek(idx_off)
    idx_raw = f.read(idx_sz)

# Parse primary index header
pos = 0
mount_point, pos = read_fstring(idx_raw, pos)
file_count = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
print(f"Files: {file_count}")
pos += 8  # hash seed
has_phi = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
phi_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
phi_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8; pos += 20
has_di = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
dir_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
dir_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8

print(f"Header: {pos} bytes")

# Parse directory index
with open(PAK_FILE, 'rb') as f:
    f.seek(dir_off)
    raw = f.read(dir_sz)
dir_data = zlib.decompress(raw) if raw[0] == 0x78 else raw
dpos = 0
dir_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4

# entry_offset_to_path
eop = {}
for d in range(dir_count):
    dn, dpos = read_fstring(dir_data, dpos)
    ec, dpos = struct.unpack_from('<i', dir_data, dpos)[0], dpos + 4
    for _ in range(ec):
        fn, dpos = read_fstring(dir_data, dpos)
        eo = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        path = (dn.rstrip('/') + '/' + fn).lstrip('/')
        eop[eo] = path  # eo = byte offset into primary index

# For each target file, try to read the FPakEntry at that offset
ENTRY_SIZE = 64  # base FPakEntry

for byte_off, path in sorted(eop.items()):
    if path not in TARGET_FILES:
        continue
    
    if byte_off + ENTRY_SIZE > len(idx_raw):
        print(f"  ❌ {path}: offset {byte_off} beyond primary index ({len(idx_raw)})")
        continue
    
    # Read FPakEntry at this byte offset in primary index
    rec = idx_raw[byte_off:byte_off+ENTRY_SIZE]
    name_hash = struct.unpack_from('<Q', rec, 0)[0]
    file_pos = struct.unpack_from('<Q', rec, 8)[0]
    file_size = struct.unpack_from('<Q', rec, 16)[0]
    file_uncomp = struct.unpack_from('<Q', rec, 24)[0]
    comp_method = struct.unpack_from('<I', rec, 32)[0]
    block_count = struct.unpack_from('<I', rec, 36)[0]
    flags = struct.unpack_from('<I', rec, 40)[0]
    
    print(f"  Entry {byte_off}: {path}")
    print(f"    pos={file_pos} size={file_size}/{file_uncomp} method={comp_method} blocks={block_count} flags={flags}")
    
    if file_pos > 0 and file_pos < fsize and file_size > 0 and file_size < 100_000_000:
        # Read file data
        with open(PAK_FILE, 'rb') as f:
            f.seek(file_pos)
            raw_data = f.read(file_size)
        
        out_path = os.path.join(OUTPUT_DIR, os.path.basename(path))
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(raw_data)
        print(f"    ✅ SAVED: {out_path} ({len(raw_data)} bytes)")
    else:
        # Maybe this is not a direct entry but an index into an entries table
        print(f"    ❌ Invalid position/size - trying as entry index")
        # Try: byte_off * ENTRY_SIZE calculation
        alt_off = pos + byte_off  # offset after header
        if alt_off + ENTRY_SIZE <= len(idx_raw):
            rec2 = idx_raw[alt_off:alt_off+ENTRY_SIZE]
            fp2 = struct.unpack_from('<Q', rec2, 8)[0]
            fs2 = struct.unpack_from('<Q', rec2, 16)[0]
            print(f"    alt: pos={fp2} size={fs2}")
