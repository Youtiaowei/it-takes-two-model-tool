#!/usr/bin/env python3
"""Extract all character files (Cody, May) from v11 PAK"""
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
    pos += 8  # pathHashSeed
    pos += 4  # hasPathHashIndex
    pos += 36  # PathHashIndex
    pos += 4  # hasDirIndex
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

pakfile = sys.argv[1]
mount, all_files = parse_pak_index(pakfile)

print(f'Mount: {mount}')
print(f'Total files: {len(all_files)}')
print()

# Find all Cody/May related files
cody_files = [(p, o) for p, o in all_files if 'cody' in p.lower()]
may_files = [(p, o) for p, o in all_files if 'may' in p.lower() or '/may/' in p.lower()]

print(f'🎯 Cody files: {len(cody_files)}')
for p, o in sorted(cody_files, key=lambda x: x[0]):
    ext = p.split('.')[-1] if '.' in p else '(dir)'
    print(f'    [{ext:8}] {p}')

print(f'\n🎯 May files: {len(may_files)}')
for p, o in sorted(may_files, key=lambda x: x[0]):
    ext = p.split('.')[-1] if '.' in p else '(dir)'
    print(f'    [{ext:8}] {p}')
