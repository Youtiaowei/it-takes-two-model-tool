#!/usr/bin/env python3
"""Search pak index for any readable paths - print them all"""
import os, struct

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')
size = os.path.getsize(pak_path)

with open(pak_path, 'rb') as f:
    f.seek(size - 204)
    foot = f.read(44)
    magic, version, idx_off, idx_sz, idx_hash = struct.unpack('<IIQQ20s', foot)
    
    f.seek(idx_off)
    idx_data = f.read(idx_sz)
    
    # Find all null-terminated strings
    strings = []
    i = 0
    while i < len(idx_data):
        null_pos = idx_data.find(b'\x00', i)
        if null_pos == -1 or null_pos - i > 500:
            i += 1
            continue
        if null_pos > i:
            s = idx_data[i:null_pos]
            try:
                text = s.decode('utf-8', errors='replace')
                if any(c in text for c in ['/', '.']) and len(text) > 5:
                    strings.append(text)
            except:
                pass
        i = null_pos + 1
    
    # Print all unique paths
    unique = sorted(set(strings))
    print(f'Found {len(unique)} unique path-like strings')
    print('=' * 80)
    for s in unique[:200]:
        print(f'  {s}')
