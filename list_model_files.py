#!/usr/bin/env python3
"""列出 Cody/May 模型相关文件（网格、骨骼、物理、材质、纹理）"""
import struct, zlib, os, sys

def parse_pak_index(pakfile):
    fsize = os.path.getsize(pakfile)
    with open(pakfile, 'rb') as f:
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
    
    with open(pakfile, 'rb') as f:
        f.seek(idx_off)
        raw = f.read(min(idx_sz, 5000000))
    
    pos = 0
    strlen = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    mount = raw[pos:pos+strlen-1].decode('utf-8', errors='replace'); pos += strlen
    file_count = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    pos += 8; pos += 4; pos += 36; pos += 4
    dir_off = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    dir_sz = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    
    with open(pakfile, 'rb') as f:
        f.seek(dir_off)
        dir_raw = f.read(min(dir_sz, 5000000))
    if dir_raw[:2] in (b'\x78\x9c', b'\x78\xda', b'\x78\x01'):
        dir_raw = zlib.decompress(dir_raw)
    
    dpos = 0
    dcount = struct.unpack_from('<i', dir_raw, dpos)[0]; dpos += 4
    files = []
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
            files.append((dirn.rstrip('/') + '/' + fn, eoff))
    return mount, files

mapak = sys.argv[1]
mount, all_files = parse_pak_index(mapak)

# Keywords for model-related files
model_keywords = ['mesh', 'skeleton', 'physics', 'material', 'texture', 'sk_', 'body', 'hair', 'cloth', '_mat']

def is_model_file(path):
    p = path.lower()
    # Only check Characters/Cody and Characters/May directories
    if 'characters/cody' not in p and 'characters/may' not in p:
        return False
    if '/animations/' in p or '/behaviour/' in p or '/audio/' in p:
        return False
    return True

# Filter
filtered = [(p, o) for p, o in all_files if is_model_file(p)]

print(f'🎯 Cody & May model-related files ({len(filtered)}):')
for p, o in sorted(filtered, key=lambda x: x[0]):
    print(f'  {p}')
