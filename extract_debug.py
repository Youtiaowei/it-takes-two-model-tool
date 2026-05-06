"""
UE4 v11 PAK extractor v5 - debug version to understand entry format
"""
import struct, os

PAK_FILE = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak"

fsize = os.path.getsize(PAK_FILE)
with open(PAK_FILE, 'rb') as f:
    f.seek(-204, 2)
    footer = f.read(44)
    magic, ver, idx_off, idx_sz, _ = struct.unpack('<IIQQ20s', footer)
    f.seek(idx_off)
    idx_raw = f.read(idx_sz)

# Decode primary index header
pos = 0
# Mount point
mlen = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
mp = idx_raw[pos:pos+mlen-1].decode('utf-8'); pos += mlen
file_count = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
pos += 8  # hash seed

has_phi = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
phi_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
phi_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
pos += 20

has_di = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
dir_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
dir_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8

print(f"Primary index header size: {pos} bytes")
print(f"Record data starts at byte {pos} in index")
print(f"Directory index at byte {dir_off - idx_off} in index")

if has_di:
    records_size = dir_off - idx_off - pos
else:
    records_size = len(idx_raw) - pos

print(f"Records area: {records_size} bytes ({records_size / 76:.0f} entries at 76 bytes)")
print(f"Records area: {records_size / 60:.0f} entries at 60 bytes)")

# The entry indices from directory index
entry_indices = [10704, 432160, 11376, 395184]
print(f"\nEntry indices: {entry_indices}")
for ei in entry_indices:
    for bpw in [60, 64, 68, 72, 76, 80, 84, 88, 92]:
        byte_off = pos + ei * bpw
        if byte_off + 60 <= len(idx_raw):
            comp_name = idx_raw[byte_off:byte_off+4]
            file_pos = struct.unpack_from('<Q', idx_raw, byte_off+4)[0]
            file_size = struct.unpack_from('<Q', idx_raw, byte_off+12)[0]
            file_uncomp = struct.unpack_from('<Q', idx_raw, byte_off+20)[0]
            if file_pos > 0 and file_pos < fsize and file_size > 0 and file_size < 100_000_000:
                print(f"  Index {ei}: bytes_per_entry={bpw}")
                print(f"     offset={byte_off}, comp_name={comp_name}, pos={file_pos}, size={file_size}/{file_uncomp}")

print(f"\nNow trying: entry indices ARE byte offsets into records area")
for ei in entry_indices:
    if ei + 60 <= records_size:
        byte_off = pos + ei
        if byte_off + 60 > len(idx_raw):
            continue
        file_pos = struct.unpack_from('<Q', idx_raw, byte_off+4)[0]
        file_size = struct.unpack_from('<Q', idx_raw, byte_off+12)[0]
        if file_pos > 0 and file_pos < fsize and file_size > 0:
            comp_name = struct.unpack_from('<4s', idx_raw, byte_off)[0]
            file_uncomp = struct.unpack_from('<Q', idx_raw, byte_off+20)[0]
            comp_method = struct.unpack_from('<I', idx_raw, byte_off+28)[0]
            block_count = struct.unpack_from('<I', idx_raw, byte_off+32)[0]
            print(f"  ✅ Index {ei}: comp_name={comp_name}, pos={file_pos}, size={file_size}/{file_uncomp}, method={comp_method}, blocks={block_count}")
        else:
            pass  # print(f"  ❌ Index {ei}: invalid pos={file_pos} or size={file_size}")

print(f"\nTrying with entry_size = 76 + block_table:")
# The actual entry structure might be: 
# FPakEntry (base, with compression blocks inline)
# For no compression: method_idx=0, blocks=0, block table is omitted
# Base = 60 bytes

cur_pos = pos
entry_num = 0
while cur_pos + 44 <= len(idx_raw) and entry_num < 50:
    file_pos = struct.unpack_from('<Q', idx_raw, cur_pos+4)[0]
    file_size = struct.unpack_from('<Q', idx_raw, cur_pos+12)[0]
    file_uncomp = struct.unpack_from('<Q', idx_raw, cur_pos+20)[0]
    
    if entry_num < 5 or entry_num in [140, 149, 5199, 5686]:
        comp_name = struct.unpack_from('<4s', idx_raw, cur_pos)[0]
        comp_method = struct.unpack_from('<I', idx_raw, cur_pos+28)[0]
        block_count = struct.unpack_from('<I', idx_raw, cur_pos+32)[0]
        flags = struct.unpack_from('<I', idx_raw, cur_pos+36)[0]
        sha1 = idx_raw[cur_pos+40:cur_pos+60].hex()
        # blocks start at cur_pos+60
        print(f"  [{entry_num}] off={cur_pos} name={comp_name} pos={file_pos} sz={file_size}/{file_uncomp} method={comp_method} blocks={block_count} flags={flags}")
    
    # Determine size: all entries in v11 have a fixed-size header + block table
    # Let's guess the size by reading the next entry's position
    saved_pos = cur_pos
    # Move past current entry
    comp_method = struct.unpack_from('<I', idx_raw, cur_pos+28)[0]
    block_count = struct.unpack_from('<I', idx_raw, cur_pos+32)[0]
    
    # Calculate entry size
    if comp_method == 0:  # No compression
        entry_sz = 60  # No block table needed
    else:
        entry_sz = 60 + block_count * 16
    
    if entry_sz <= 0:
        entry_sz = 60
    cur_pos += entry_sz
    entry_num += 1
