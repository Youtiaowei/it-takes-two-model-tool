#!/usr/bin/env python3
"""重新解析 pak 索引，找到 Cody/May 角色模型文件"""
import struct, os

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')
size = os.path.getsize(pak_path)

with open(pak_path, 'rb') as f:
    # Read footer at -204 bytes
    f.seek(size - 204)
    foot = f.read(44)
    magic, version, idx_off, idx_sz, idx_hash = struct.unpack('<IIQQ20s', foot)
    print(f'Version: {version}, Index offset: {idx_off}, Index size: {idx_sz}')
    
    # Read index
    f.seek(idx_off)
    idx = f.read(idx_sz)
    
    # Parse mount point
    mount_len = struct.unpack('<I', idx[0:4])[0]
    mount_raw = idx[4:4+mount_len]
    mount_point = mount_raw.split(b'\x00')[0].decode('utf-8', errors='replace')
    print(f'Mount point: {mount_point}')
    
    pos = 4 + mount_len
    
    # Skip directory index and go to file entries
    # v11 structure: mount_len + mount + [directory entries...] + [file entries...]
    # Let's try different structures
    
    print(f'\nHex dump at pos {pos}:')
    print(' '.join(f'{b:02x}' for b in idx[pos:pos+32]))
    
    # Try: uint64 file_count at pos
    file_count = struct.unpack('<Q', idx[pos:pos+8])[0]
    print(f'\nIf file_count at +0: {file_count}')
    
    # Try: directory_count + file_count
    dir_count = struct.unpack('<I', idx[pos:pos+4])[0]
    print(f'If dir_count at +0: {dir_count}')
    
    # Try at +4
    val_at_4 = struct.unpack('<I', idx[pos+4:pos+8])[0]
    print(f'uint32 at +4: {val_at_4}')
    
    val_at_8 = struct.unpack('<Q', idx[pos+8:pos+16])[0]
    print(f'uint64 at +8: {val_at_8}')
    
    # Let's try to walk the directory index
    # Typical v11 structure:
    # [mount_len][mount_string]
    # [dir_count(uint32)][file_count(uint32)]
    # [directories...][files...]
    
    pos = 4 + mount_len
    dir_count = struct.unpack('<I', idx[pos:pos+4])[0]
    file_count = struct.unpack('<I', idx[pos+4:pos+8])[0]
    print(f'\nDirectories: {dir_count}, Files: {file_count}')
    
    # Skip directory entries (each: offset(uint64) + path_length(uint32) + path)
    pos += 8  # skip counts
    for d in range(dir_count):
        dir_off = struct.unpack('<Q', idx[pos:pos+8])[0]
        dir_path_len = struct.unpack('<I', idx[pos+8:pos+12])[0]
        dir_path_raw = idx[pos+12:pos+12+dir_path_len]
        dir_path = dir_path_raw.split(b'\x00')[0].decode('utf-8', errors='replace')
        pos += 12 + dir_path_len
        if d < 10:
            print(f'  Dir {d}: {dir_path}')
    
    print(f'\nAfter dirs, pos={pos}')
    
    # Now parse file entries
    # Each file: [name_hash(uint32)][offset(int64)][size(int64)][compressed_size(int64)][flags(uint32)][path_len(uint32)][path]
    
    cody_may_files = []
    total_entries = 0
    
    for f_idx in range(min(file_count, 50000)):
        if pos + 36 > len(idx):
            break
        
        name_hash = struct.unpack('<I', idx[pos:pos+4])[0]
        file_offset = struct.unpack('<Q', idx[pos+4:pos+12])[0]
        file_size = struct.unpack('<Q', idx[pos+12:pos+20])[0]
        comp_size = struct.unpack('<Q', idx[pos+20:pos+28])[0]
        flags = struct.unpack('<I', idx[pos+28:pos+32])[0]
        path_len = struct.unpack('<I', idx[pos+32:pos+36])[0]
        
        if path_len > 0 and path_len < 500 and pos + 36 + path_len <= len(idx):
            path_raw = idx[pos+36:pos+36+path_len]
            path = path_raw.rstrip(b'\x00').decode('utf-8', errors='replace')
        else:
            path = f'<invalid_len={path_len}>'
        
        total_entries += 1
        
        pl = path.lower()
        if ('cody' in pl and ('mesh' in pl or 'model' in pl or 'skeleton' in pl or 'physics' in pl or pl.endswith('.uasset') or pl.endswith('.uexp'))) or \
           ('may_' in pl and ('mesh' in pl or 'model' in pl or 'skeleton' in pl or 'physics' in pl or pl.endswith('.uasset') or pl.endswith('.uexp'))):
            cody_may_files.append((file_offset, file_size, comp_size, flags, path))
        
        pos += 36 + path_len
    
    print(f'\nParsed {total_entries} file entries total')
    print(f'\nCody/May related files ({len(cody_may_files)}):')
    for off, sz, csz, fl, path in cody_may_files:
        label = ''
        if 'skeleton' in path.lower(): label = ' [SKELETON]'
        elif 'mesh' in path.lower(): label = ' [MESH]'
        elif 'physics' in path.lower(): label = ' [PHYSICS]'
        print(f'  {sz:>10,}B  {off:>12,}  {path}{label}')
