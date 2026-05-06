"""
UE4 v11 PAK Extractor v6 - corrected FPakEntry format
FPakEntry: NameHash(8) + Pos(8) + Size(8) + Uncomp(8) + MethodIdx(4) + Blocks(4) + Flags(4) + SHA1(20) = 64 bytes base
If compressed: + block_count * 16 bytes block table
If uncompressed (method=0): no block table, just 64 bytes
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
print(f"PAK: {os.path.basename(PAK_FILE)} ({fsize/(1024**3):.1f} GB)")

# Read footer
with open(PAK_FILE, 'rb') as f:
    f.seek(-204, 2)
    footer = f.read(44)
    magic, ver, idx_off, idx_sz, _ = struct.unpack('<IIQQ20s', footer)
    f.seek(idx_off)
    idx_raw = f.read(idx_sz)

# Parse primary index header
pos = 0
mount_point, pos = read_fstring(idx_raw, pos)
file_count = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
print(f"Mount: {mount_point}")
print(f"Files: {file_count}")
pos += 8  # hash seed

# Skip through headers to find records
has_phi = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
phi_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
phi_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
pos += 20

has_di = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
dir_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
dir_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8

print(f"Header ends at byte {pos}")
print(f"Records area starts at byte {pos} in primary index")

# Parse directory index
with open(PAK_FILE, 'rb') as f:
    f.seek(dir_off)
    dir_raw = f.read(dir_sz)
if dir_raw[0] == 0x78:
    dir_data = zlib.decompress(dir_raw)
else:
    dir_data = dir_raw

dpos = 0
dir_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4

# Build entry index -> file path map
entry_to_path = {}
for d in range(dir_count):
    dirname, dpos = read_fstring(dir_data, dpos)
    ent_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
    for e in range(ent_count):
        fname, dpos = read_fstring(dir_data, dpos)
        ent_idx = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        path = (dirname.rstrip('/') + '/' + fname).lstrip('/')
        entry_to_path[ent_idx] = path

# Now parse file records
# FPakEntry (v11): 8+8+8+8+4+4+4+20 = 64 bytes base
# Then: if block_count > 0, block table of block_count * 16 bytes
ENTRY_BASE = 64
records_raw = idx_raw[pos:]

print(f"\nParsing {file_count} file records ({len(records_raw)} bytes)...")

cur = 0
entry_idx = 0
found = {}

while cur + ENTRY_BASE <= len(records_raw) and entry_idx <= max(entry_to_path.keys()):
    name_hash = struct.unpack_from('<Q', records_raw, cur)[0]
    file_pos = struct.unpack_from('<Q', records_raw, cur+8)[0]
    file_size = struct.unpack_from('<Q', records_raw, cur+16)[0]
    file_uncomp = struct.unpack_from('<Q', records_raw, cur+24)[0]
    comp_method = struct.unpack_from('<I', records_raw, cur+32)[0]
    block_count = struct.unpack_from('<I', records_raw, cur+36)[0]
    flags = struct.unpack_from('<I', records_raw, cur+40)[0]
    sha1 = records_raw[cur+44:cur+64]
    
    # Check if this entry looks valid
    # For It Takes Two assets: sizes should be positive and files within pak range
    is_valid = (file_pos > 0 and file_pos < fsize and file_size > 0 and file_size < 10_000_000)
    
    # Calculate entry size
    if block_count > 0 and comp_method > 0:
        entry_size = ENTRY_BASE + block_count * 16
    else:
        entry_size = ENTRY_BASE
    
    if entry_idx in entry_to_path:
        path = entry_to_path[entry_idx]
        valid_mark = "✅" if is_valid else "❌"
        if is_valid:
            print(f"  [{entry_idx}] {valid_mark} {path} pos={file_pos} size={file_size}/{file_uncomp} method={comp_method} blocks={block_count}")
        
        if is_valid and path in TARGET_FILES:
            # Extract!
            with open(PAK_FILE, 'rb') as f:
                f.seek(file_pos)
                raw_data = f.read(file_size)
            
            out_path = os.path.join(OUTPUT_DIR, os.path.basename(path))
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            with open(out_path, 'wb') as f:
                f.write(raw_data)
            print(f"     ✅ SAVED: {out_path} ({len(raw_data)} bytes)")
            found[path] = out_path
    
    elif is_valid and entry_idx < 5:
        print(f"  [{entry_idx}] (unknown) pos={file_pos} size={file_size}/{file_uncomp}")
    
    cur += entry_size
    entry_idx += 1
    if entry_idx % 10000 == 0:
        print(f"  ... parsed {entry_idx}/{file_count} records")

print(f"\n{'='*60}")
print(f"Extraction complete!")
print(f"Files extracted: {len(found)}")
for path, out in found.items():
    sz = os.path.getsize(out)
    print(f"  ✅ {path} -> {os.path.basename(out)} ({sz} bytes)")
