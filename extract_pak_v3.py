"""
UE4 v11 PAK file extractor v3 - reads directory index from file properly
"""
import struct, os, sys, zlib

PAK_FILE = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak"
OUTPUT_DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"
TARGET_PATHS = [
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

def parse_pak(pakfile):
    print(f"Opening: {pakfile}")
    fsize = os.path.getsize(pakfile)
    
    with open(pakfile, 'rb') as f:
        # Read footer
        f.seek(-204, 2)
        footer = f.read(44)
        magic, ver, idx_off, idx_sz, _ = struct.unpack('<IIQQ20s', footer)
        assert magic == 0x5A6F12E1
        print(f"  Version: {ver}, Index: {idx_off}, Size: {idx_sz}")
        
        # Read primary index
        f.seek(idx_off)
        idx_raw = f.read(idx_sz)
    
    # Parse primary index header
    pos = 0
    mount_point, pos = read_fstring(idx_raw, pos)
    print(f"  Mount: {mount_point}")
    
    file_count = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
    print(f"  Files: {file_count}")
    pos += 8  # hash seed
    
    # PathHashIndex
    has_phi = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
    phi_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    phi_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    pos += 20
    
    # DirectoryIndex
    has_di = struct.unpack_from('<i', idx_raw, pos)[0]; pos += 4
    dir_off = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    dir_sz = struct.unpack_from('<Q', idx_raw, pos)[0]; pos += 8
    
    print(f"  DirIndex: off={dir_off}, sz={dir_sz}, has={bool(has_di)}")
    print(f"  Records start at byte {pos} in primary index")
    
    # Read directory index from file
    with open(pakfile, 'rb') as f:
        f.seek(dir_off)
        dir_raw = f.read(dir_sz)
    
    # Decompress if needed
    if dir_raw and dir_raw[0] == 0x78:
        dir_data = zlib.decompress(dir_raw)
        print(f"  DirIndex: decompressed {dir_sz} -> {len(dir_data)}")
    else:
        dir_data = dir_raw
        print(f"  DirIndex: {len(dir_data)} bytes (uncompressed)")
    
    # Parse directories
    dpos = 0
    dir_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
    print(f"  Directories: {dir_count}")
    
    # Build entry_idx -> file_path mapping
    entry_map = {}
    for d in range(dir_count):
        dirname, dpos = read_fstring(dir_data, dpos)
        entry_count = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        for e in range(entry_count):
            fname, dpos = read_fstring(dir_data, dpos)
            ent_idx = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
            full_path = (dirname.rstrip('/') + '/' + fname).lstrip('/')
            entry_map[ent_idx] = full_path
    
    print(f"  Total entries: {len(entry_map)}")
    
    # Now we need to find the file records. In v11 PAK, after the primary index header,
    # there are file records (FPakEntry). Each record's size is:
    # base: 4(comp method name) + 8(pos) + 8(size) + 8(uncomp) + 4(method) + 4(blocks) + 4(flags) + 20(SHA1) = 60
    # + compression blocks (if any): blocks * (8 + 8)
    # But in v11 with default settings (no compression), blocks=1, so each entry is 60 + 16 = 76 bytes
    
    # The directory index gives us entry_indices, which are the INDEX into the file records table
    # Each entry has fixed size in v11 (probably)
    
    # Let's scan through records and find matching entries
    records_raw = idx_raw[pos:dir_off - idx_off if has_di else len(idx_raw)]
    
    # Find target files
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    found_count = 0
    
    for ent_idx, path in sorted(entry_map.items()):
        if path in TARGET_PATHS:
            print(f"\n  ✅ {path} (index={ent_idx})")
            found_count += 1
            
            # Try to find the entry at various byte offsets
            # In v11, entries might have variable sizes depending on compression blocks
            # Let's try a heuristic: scan forward from the start of records
            rpos = 0
            current_entry = 0
            while current_entry <= ent_idx and rpos + 60 < len(records_raw):
                comp_name = struct.unpack_from('<4s', records_raw, rpos)[0]
                file_pos = struct.unpack_from('<Q', records_raw, rpos+4)[0]
                file_size = struct.unpack_from('<Q', records_raw, rpos+12)[0]
                file_uncomp = struct.unpack_from('<Q', records_raw, rpos+20)[0]
                comp_method = struct.unpack_from('<I', records_raw, rpos+28)[0]
                block_count = struct.unpack_from('<I', records_raw, rpos+32)[0]
                flags = struct.unpack_from('<I', records_raw, rpos+36)[0]
                
                if current_entry == ent_idx:
                    print(f"     pos={file_pos} size={file_size}/{file_uncomp} method={comp_method} blocks={block_count}")
                    
                    if file_pos > 0 and file_size > 0 and file_pos + file_size <= fsize:
                        with open(pakfile, 'rb') as f:
                            f.seek(file_pos)
                            raw_data = f.read(file_size)
                        
                        # Handle compression
                        if comp_method == 0 or comp_method == 10:  # None
                            data = raw_data
                        elif comp_method == 1:  # Zlib
                            # Might need to decompress per-block
                            data = raw_data  # TBD
                        else:
                            print(f"     Unsupported compression: {comp_method}")
                            data = raw_data
                        
                        out_path = os.path.join(OUTPUT_DIR, os.path.basename(path))
                        with open(out_path, 'wb') as f:
                            f.write(data)
                        print(f"     ✅ Saved: {out_path} ({len(data)} bytes)")
                    else:
                        print(f"     ❌ Invalid file position or size")
                    break
                
                # Advance to next entry
                # v11 entry: base 60 + (block_count * 16) for compression blocks
                if block_count > 0:
                    rpos += 60 + block_count * 16
                elif file_size > 0:
                    # No compression blocks listed, assume 1
                    rpos += 60 + 16
                else:
                    rpos += 76  # fallback
                current_entry += 1
    
    print(f"\nFound {found_count} target files")
    print(f"Output: {OUTPUT_DIR}")

if __name__ == '__main__':
    parse_pak(PAK_FILE)
