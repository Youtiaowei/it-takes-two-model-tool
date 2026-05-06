#!/usr/bin/env python3
"""Try to extract Cody/May .uasset files using a brute-force approach"""
import struct, os, sys

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')
output_dir = 'extracted_chars'

# First, find the footer and parse the primary index
fsize = os.path.getsize(pak_path)

with open(pak_path, 'rb') as f:
    # Find footer
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
        print("No valid footer found")
        sys.exit(1)
    
    print(f'Footer: v{version}, idx_off={idx_off:,}, idx_sz={idx_sz:,}')
    
    # Read primary index
    f.seek(idx_off)
    raw = f.read(min(idx_sz, 5000000))
    
    pos = 0
    strlen = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    mount = raw[pos:pos+strlen-1].decode('utf-8', errors='replace'); pos += strlen
    print(f'Mount: {mount}')
    
    file_count = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    print(f'File count: {file_count}')
    
    seed = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    has_hash = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    print(f'HasPathHash: {has_hash}')
    
    if has_hash:
        hash_off = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
        hash_sz = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
        pos += 20
        print(f'PathHash: off={hash_off:,}, sz={hash_sz:,}')
    
    has_dir = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    print(f'HasDir: {has_dir}')
    dir_off = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    dir_sz = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    pos += 20
    print(f'Dir: off={dir_off:,}, sz={dir_sz:,}')
    
    # Read directory index  
    f.seek(dir_off)
    dir_raw = f.read(min(dir_sz, 5000000))
    try:
        if dir_raw[:2] in (b'\x78\x9c', b'\x78\xda', b'\x78\x01'):
            dir_raw = zlib.decompress(dir_raw)
    except: pass
    
    dpos = 0
    dcount = struct.unpack_from('<i', dir_raw, dpos)[0]; dpos += 4
    
    # Walk directories and find Cody/May files
    target_files = {}
    for d in range(dcount):
        dlen = struct.unpack_from('<i', dir_raw, dpos)[0]; dpos += 4
        dirn = '' if dlen == 0 else dir_raw[dpos:dpos+abs(dlen)-1].decode('utf-8' if dlen>0 else 'utf-16-le', errors='replace')
        dpos += abs(dlen)
        ec = struct.unpack_from('<i', dir_raw, dpos)[0]; dpos += 4
        for e in range(ec):
            flen = struct.unpack_from('<i', dir_raw, dpos)[0]; dpos += 4
            fn = dir_raw[dpos:dpos+abs(flen)-1].decode('utf-8' if flen>0 else 'utf-16-le', errors='replace') if flen != 0 else ''
            dpos += abs(flen)
            eoff = struct.unpack_from('<i', dir_raw, dpos)[0]; dpos += 4
            
            full_path = dirn.rstrip('/') + '/' + fn
            pl = full_path.lower()
            
            # Only interested in Cody/May .uasset and .uexp files
            if 'characters/cody' in pl or 'characters/may' in pl:
                if full_path.endswith('.uasset') or full_path.endswith('.uexp'):
                    if 'cody' in pl or 'may' in pl:
                        # Skip animations, audio, doll, LOD settings
                        if 'animation' not in pl and 'audio' not in pl and 'doll' not in pl and 'lod' not in pl and 'texture' not in pl and 'material' not in pl and 'faceposes' not in pl:
                            target_files[full_path] = eoff
    
    print(f'\nTarget files: {len(target_files)}')
    for p, eo in sorted(target_files.items()):
        print(f'  {p} (entry={eo})')

import zlib
