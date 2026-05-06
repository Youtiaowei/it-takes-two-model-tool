#!/usr/bin/env python3
"""Extract all character model files from It Takes Two v11 PAK archives"""

import struct, zlib, os, sys

def parse_pak_index(pakfile):
    """Parse v11 PAK directory index and return list of (path, file_entry_offset) tuples"""
    fsize = os.path.getsize(pakfile)
    
    with open(pakfile, 'rb') as f:
        # Find the footer (search for magic at end of file)
        f.seek(-300, 2)
        end_data = f.read(300)
        
        for i in range(len(end_data)):
            magic = struct.unpack_from('<I', end_data, i)[0]
            if magic == 0x5A6F12E1 and i + 4 < len(end_data):
                version = struct.unpack_from('<I', end_data, i+4)[0]
                if 1 <= version <= 13:
                    idx_off = struct.unpack_from('<Q', end_data, i+8)[0]
                    idx_sz = struct.unpack_from('<Q', end_data, i+16)[0]
                    if 0 < idx_off < fsize and idx_sz > 0:
                        break
        else:
            raise Exception("Could not find valid PAK footer")
    
    print(f"  Version: {version}, Index: offset={idx_off}, size={idx_sz} ({idx_sz/1024:.1f} KB)")
    
    # Read primary index
    with open(pakfile, 'rb') as f:
        f.seek(idx_off)
        raw = f.read(min(idx_sz, 5000000))
    
    # Parse primary index
    pos = 0
    strlen = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    mount = raw[pos:pos+strlen-1].decode('utf-8', errors='replace'); pos += strlen
    file_count = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    pos += 8  # pathHashSeed
    pos += 4  # hasPathHashIndex (int32)
    pos += 36  # PathHashIndex: offset(8) + size(8) + hash(20)
    pos += 4  # hasDirIndex (int32)
    dir_off = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    dir_sz = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    
    # Read directory index
    with open(pakfile, 'rb') as f:
        f.seek(dir_off)
        dir_raw = f.read(min(dir_sz, 5000000))
    
    # Try zlib decompression
    if dir_raw[0] == 0x78:
        dir_data = zlib.decompress(dir_raw)
    else:
        dir_data = dir_raw
    
    # Parse directory entries
    dpos = 0
    dcount = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
    
    files = []
    for d in range(dcount):
        dlen = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        dirn = '' if dlen == 0 else dir_data[dpos:dpos+abs(dlen)-1].decode('utf-8' if dlen>0 else 'utf-16-le', errors='replace')
        dpos += abs(dlen)
        ec = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
        for e in range(ec):
            flen = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
            fn = dir_data[dpos:dpos+abs(flen)-1].decode('utf-8' if flen>0 else 'utf-16-le', errors='replace') if flen != 0 else ''
            dpos += abs(flen)
            eoff = struct.unpack_from('<i', dir_data, dpos)[0]; dpos += 4
            files.append((dirn.rstrip('/') + '/' + fn, eoff))
    
    print(f"  Total files: {len(files)}")
    return mount, files


def extract_file(pakfile, all_files, target_path, output_dir):
    """Extract a specific file from the PAK. all_files is list of (path, entry_offset)."""
    # Find the target file
    entry = None
    for path, entry_offset in all_files:
        if path == target_path:
            entry = (path, entry_offset)
            break
    
    if not entry:
        print(f"  NOT FOUND: {target_path}")
        return False
    
    path, entry_offset = entry
    
    # Read the FPakEntry at entry_offset in the encoded pak entries section
    # (This is complex - we'd need the full encoded entries data structure)
    # For now, we can read the raw .uasset data from the file
    
    # Actually, the directory index only gives us an offset into the encoded entries table,
    # not the actual file data offset. We need to parse the FPakEntry structure.
    
    print(f"  FOUND: {path} (entry offset: {entry_offset})")
    return True


def main():
    pakfile = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else 'extracted_chars'
    
    os.makedirs(output, exist_ok=True)
    
    mount, all_files = parse_pak_index(pakfile)
    
    # Find Cody and May model files
    wanted = []
    for path, _ in all_files:
        p = path.lower()
        # Main model files
        if path == 'Nuts/Content/Characters/Cody/Cody.uasset' or \
           path == 'Nuts/Content/Characters/Cody/Cody.uexp' or \
           path == 'Nuts/Content/Characters/May/May.uasset' or \
           path == 'Nuts/Content/Characters/May/May.uexp':
            wanted.append(path)
    
    print(f"\n  Wanted files: {len(wanted)}")
    for w in wanted:
        print(f"    {w}")


if __name__ == '__main__':
    main()
