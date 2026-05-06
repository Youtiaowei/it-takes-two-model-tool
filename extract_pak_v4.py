"""
UE4 v11 PAK extractor v4 - entry scanning approach
Scans the file offsets in the PAK to find valid file records
"""
import struct, os, sys, zlib

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
    s = data[pos:pos+abslen-1].decode(enc, errors='replace')
    pos += abslen
    return s, pos

print("=" * 60)
print("UE4 v11 PAK Extractor - It Takes Two")
print("=" * 60)

fsize = os.path.getsize(PAK_FILE)
print(f"\nPAK: {os.path.basename(PAK_FILE)} ({fsize/(1024**3):.1f} GB)")

with open(PAK_FILE, 'rb') as f:
    f.seek(-204, 2)
    footer = f.read(44)
    magic, ver, idx_off, idx_sz, _ = struct.unpack('<IIQQ20s', footer)
    print(f"Footer: ver={ver}, idx_off={idx_off}, idx_sz={idx_sz}")
    
    f.seek(idx_off)
    idx_raw = f.read(idx_sz)

pos = 0
mount_point, pos = read_fstring(idx_raw, pos)
file_count = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
print(f"Mount: {mount_point}")
print(f"Files: {file_count}")
pos += 8  # hash seed

# Skip PathHashIndex
has_phi = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
phi_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
phi_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
pos += 20

# Skip DirectoryIndex
has_di = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
dir_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
dir_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8

print(f"\nParsing directory index...")
with open(PAK_FILE, 'rb') as f:
    f.seek(dir_off)
    dir_raw = f.read(dir_sz)

if dir_raw[0] == 0x78:
    dir_data = zlib.decompress(dir_raw)
else:
    dir_data = dir_raw

dpos = 0
dir_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4

# Build entry map
entry_to_path = {}
dir_names = set()
for d in range(dir_count):
    dirname, dpos = read_fstring(dir_data, dpos)
    dir_names.add(dirname)
    entry_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
    for e in range(entry_count):
        fname, dpos = read_fstring(dir_data, dpos)
        ent_idx = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        path = (dirname.rstrip('/') + '/' + fname).lstrip('/')
        entry_to_path[ent_idx] = path

# Now find target entries
target_entries = [(idx, path) for idx, path in entry_to_path.items() if path in TARGET_FILES]
print(f"\nFound {len(target_entries)} target entries")

# Now scan file records. In v11 PAK, the file records come after the primary index header.
# Each FPakEntry has:
#   CompressionMethod (4 bytes, method name like "None" or "Zlib")
#   Position (8 bytes, offset in pak)
#   Size (8 bytes, compressed size)
#   UncompressedSize (8 bytes)
#   CompressionMethodIndex (4 bytes, 0=None, 1=Zlib)
#   CompressionBlockCount (4 bytes)
#   Flags (4 bytes, bitfield)
#   SHA1 (20 bytes)
# Then for each compression block: CompressedSize (8) + UncompressedSize (8)

# Let's parse all entries by scanning
entries_data = idx_raw[pos:]

print(f"\nScanning file records ({len(entries_data)} bytes)...")

# Process entries in order
record_start = 0
current_idx = 0
found_data = {}

while record_start + 60 <= len(entries_data) and current_idx <= max(entry_to_path.keys()):
    # Check if this looks like a valid entry (position should be within file)
    file_pos = struct.unpack_from('<Q', entries_data, record_start+4)[0]
    file_size = struct.unpack_from('<Q', entries_data, record_start+12)[0]
    file_uncomp = struct.unpack_from('<Q', entries_data, record_start+20)[0]
    comp_method = struct.unpack_from('<I', entries_data, record_start+28)[0]
    block_count = struct.unpack_from('<I', entries_data, record_start+32)[0]
    
    # Validate: position should be reasonable, size should be reasonable
    if current_idx in entry_to_path and entry_to_path[current_idx] in TARGET_FILES:
        path = entry_to_path[current_idx]
        print(f"\n  [{current_idx}] {path}")
        print(f"     pos={file_pos} size={file_size}/{file_uncomp} method={comp_method} blocks={block_count}")
        
        if file_pos > 100 and file_size > 0 and file_pos + file_size <= fsize:
            with open(PAK_FILE, 'rb') as f:
                f.seek(file_pos)
                raw_data = f.read(file_size)
            
            out_path = os.path.join(OUTPUT_DIR, os.path.basename(path))
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # For UE4 .uasset: strip trailing hash before data
            # The actual file data might have trailing bytes
            if file_uncomp > 0 and file_size >= file_uncomp:
                data = raw_data[:file_uncomp]
            else:
                data = raw_data
            
            with open(out_path, 'wb') as f:
                f.write(data)
            print(f"     ✅ Saved: {out_path} ({len(data)} bytes)")
            found_data[path] = (out_path, len(data))
    
    # Calculate entry size
    entry_base_size = 60
    block_table_size = block_count * 16 if block_count > 0 else 0
    entry_total = entry_base_size + block_table_size
    
    record_start += entry_total
    current_idx += 1

print(f"\n{'='*60}")
print(f"Extraction complete!")
print(f"Found {len(found_data)} files:")
for path, (out_path, size) in found_data.items():
    print(f"  ✅ {path} -> {os.path.basename(out_path)} ({size} bytes)")
print(f"Output: {OUTPUT_DIR}")
