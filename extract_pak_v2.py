"""
UE4 v11 PAK file extractor - extract specific files from It Takes Two
Uses Directory Index for plaintext filenames + entry offsets
"""
import struct, os, sys, zlib, json

PAK_FILE = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak"
OUTPUT_DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"

# Target files to extract
TARGET_PATHS = [
    "Nuts/Content/Characters/Cody/Cody.uasset",
    "Nuts/Content/Characters/Cody/Cody.uexp",
    "Nuts/Content/Characters/May/May.uasset",
    "Nuts/Content/Characters/May/May.uexp",
]

def read_fstring(data, pos):
    """Read UE4 FString"""
    dlen = struct.unpack_from('<i', data, pos)[0]; pos += 4
    if dlen == 0:
        return '', pos
    abslen = abs(dlen)
    enc = 'utf-16-le' if dlen < 0 else 'utf-8'
    s = data[pos:pos+abslen-1].decode(enc, errors='replace')
    pos += abslen
    return s, pos

def parse_pak(pakfile):
    print(f"Opening: {pakfile}")
    fsize = os.path.getsize(pakfile)
    
    with open(pakfile, 'rb') as f:
        # Read footer (at -204 for v11)
        f.seek(-204, 2)
        footer = f.read(44)
        magic, version, idx_off, idx_sz, idx_sha = struct.unpack('<IIQQ20s', footer)
        assert magic == 0x5A6F12E1, f"Bad magic: 0x{magic:08x}"
        print(f"  Version: {version}, Index: {idx_off}, Size: {idx_sz}")
        
        # Read primary index
        f.seek(idx_off)
        idx_raw = f.read(idx_sz)
    
    pos = 0
    mount_point, pos = read_fstring(idx_raw, pos)
    print(f"  Mount: {mount_point}")
    
    file_count = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
    print(f"  Files: {file_count}")
    
    path_hash_seed = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    
    # Path Hash Index
    has_phi = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
    phi_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    phi_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    pos += 20  # SHA1
    
    # Directory Index
    has_di = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
    dir_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    dir_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    
    print(f"  HasDirIndex: {bool(has_di)}, DirIndex: {dir_off}, {dir_sz}")
    
    # === Now read encoded entries (file table) ===
    # Entries start right after the directory index info in primary index
    entries_start = pos
    entry_size = 4 + 8 + 8 + 8 + 4 + 4 + 4 + 20  # comp method name(4) + pos(8) + size(8) + uncomp(8) + comp_method(4) + block_count(4) + flags(4) + sha(20)
    # Actually v11 entry format is slightly different
    # Let's read raw bytes from entries_start to dir_off (or phi_off if it comes first)
    
    # The file records are between primary index header and directory index / path hash index
    records_data = idx_raw[entries_start:min(dir_off, phi_off) if has_di and has_phi else 
                           (dir_off if has_di else phi_off)]
    
    print(f"  Records area: {entries_start} -> {entries_start + len(records_data)} ({len(records_data)} bytes)")
    
    # Parse directory index
    dir_raw = idx_raw[dir_off - idx_off:dir_off - idx_off + dir_sz]
    if dir_raw[0] == 0x78:
        dir_data = zlib.decompress(dir_raw)
    else:
        dir_data = dir_raw
    
    dpos = 0
    dir_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
    print(f"  Directories: {dir_count}")
    
    # Parse directory entries
    entry_offsets = {}  # entry_index -> file_path
    for d in range(dir_count):
        dirname, dpos = read_fstring(dir_data, dpos)
        entry_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        for e in range(entry_count):
            fname, dpos = read_fstring(dir_data, dpos)
            ent_idx = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
            full_path = (dirname.rstrip('/') + '/' + fname).lstrip('/')
            entry_offsets[ent_idx] = full_path
    
    # Now parse file records
    # v11 FPakEntry: size varies by flags and compression blocks
    # Let's try a simpler approach: read at fixed offsets and see if the sizes match
    
    # Actually, let me try using the OffsetInFile from the record
    # First read some raw records to understand the format
    print(f"\n  Sample records (first 5):")
    sample_raw = records_data[:200]
    sp = 0
    for i in range(5):
        fmt = '<4s Q Q Q I I I 20s'  # comp_flag + pos + size + uncomp + method + blocks + flags + sha
        try:
            comp_flag, pos_in_pak, size, uncomp_sz, comp_method, block_count, flags, sha = \
                struct.unpack_from(fmt, records_data, sp)
            print(f"    [{i}] pos={pos_in_pak} size={size}/{uncomp_sz} method={comp_method} blocks={block_count}")
            sp += struct.calcsize(fmt)
        except:
            break
    
    # Now try to find and extract target files
    print(f"\n  Searching for target files...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    bytes_per_entry = 64  # approximate for v11
    
    for ent_idx, path in entry_offsets.items():
        if path in TARGET_PATHS:
            print(f"  ✅ Found: {path} (entry={ent_idx})")
            
            # Calculate byte offset into records
            entry_byte_off = ent_idx * bytes_per_entry
            
            if entry_byte_off + 64 > len(records_data):
                # try different approach - scan for matching pos
                print(f"     Trying direct scan...")
                for i in range(0, len(records_data) - 64, 4):
                    try:
                        comp_flag, pos_in_pak = struct.unpack_from('<4s Q', records_data, i)
                        sz = struct.unpack_from('<Q', records_data, i+12)[0]
                        if sz > 0 and sz < 100_000_000:
                            # Could be valid
                            pass
                    except:
                        break
                continue
            
            # Read entry
            comp_flag = struct.unpack_from('<4s', records_data, entry_byte_off)[0]
            entry_pos = struct.unpack_from('<Q', records_data, entry_byte_off+4)[0]
            entry_size = struct.unpack_from('<Q', records_data, entry_byte_off+12)[0]
            entry_uncomp = struct.unpack_from('<Q', records_data, entry_byte_off+20)[0]
            entry_method = struct.unpack_from('<I', records_data, entry_byte_off+28)[0]
            entry_blocks = struct.unpack_from('<I', records_data, entry_byte_off+32)[0]
            entry_flags = struct.unpack_from('<I', records_data, entry_byte_off+36)[0]
            
            print(f"     pos_in_pak={entry_pos} size={entry_size} uncomp={entry_uncomp} method={entry_method}")
            
            if entry_pos > 0 and entry_size > 0 and entry_pos + entry_size <= fsize:
                # Read file data
                with open(pakfile, 'rb') as f:
                    f.seek(entry_pos)
                    raw_data = f.read(entry_size)
                
                # Handle compression blocks
                if entry_method == 0:
                    data = raw_data
                elif entry_method == 1:
                    data = zlib.decompress(raw_data)
                else:
                    print(f"     Unsupported compression: {entry_method}")
                    continue
                
                # Save to output
                out_path = os.path.join(OUTPUT_DIR, os.path.basename(path))
                with open(out_path, 'wb') as f:
                    f.write(data)
                print(f"     ✅ Saved: {out_path} ({len(data)} bytes)")
    
    print(f"\nDone! Output: {OUTPUT_DIR}")
    for p in os.listdir(OUTPUT_DIR):
        fp = os.path.join(OUTPUT_DIR, p)
        print(f"  {p}: {os.path.getsize(fp)} bytes")

if __name__ == '__main__':
    parse_pak(PAK_FILE)
