#!/usr/bin/env python3
"""Complete UE4 v11 PAK extractor"""
import struct, zlib, os, sys

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')
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
    
    print(f'Footer: v{version}, idx_off={idx_off}, idx_sz={idx_sz}')
    
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
        print(f'PathHash: off={hash_off}, sz={hash_sz}')
    
    has_dir = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    print(f'HasDir: {has_dir}')
    dir_off = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    dir_sz = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    pos += 20
    print(f'Dir: off={dir_off}, sz={dir_sz}')
    
    remaining = len(raw) - pos
    print(f'Remaining bytes: {remaining}')
    
    # Read directory index
    f.seek(dir_off)
    dir_raw = f.read(min(dir_sz, 5000000))
    try:
        if dir_raw[:2] in (b'\x78\x9c', b'\x78\xda', b'\x78\x01'):
            dir_raw = zlib.decompress(dir_raw)
            print(f'Dir decompressed: {len(dir_raw)} bytes')
    except: pass
    
    # Parse directories
    dpos = 0
    dcount = struct.unpack_from('<i', dir_raw, dpos)[0]; dpos += 4
    print(f'Directories: {dcount}')
    
    dir_entries = []  # (dir_name, file_name, entry_offset)
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
            dir_entries.append((dirn.rstrip('/') + '/' + fn, eoff))
    
    print(f'Directory entries: {len(dir_entries)}')
    
    # Now check for encoded entries
    if remaining > 0:
        # There should be EncodedEntries info
        pos_in_raw = len(raw) - remaining
        has_enc = struct.unpack_from('<i', raw, pos_in_raw)[0]
        print(f'HasEncodedEntries: {has_enc}')
        if has_enc:
            enc_off = struct.unpack_from('<Q', raw, pos_in_raw+4)[0]
            enc_sz = struct.unpack_from('<Q', raw, pos_in_raw+12)[0]
            print(f'Encoded: off={enc_off}, sz={enc_sz}')
            
            f.seek(enc_off)
            enc_data = f.read(min(enc_sz, 5000000))
            try:
                if enc_data[:2] in (b'\x78\x9c', b'\x78\xda', b'\x78\x01'):
                    enc_data = zlib.decompress(enc_data)
                    print(f'Encoded decompressed: {len(enc_data)} bytes')
            except: pass
            
            # Parse first few to understand the structure
            epos = 0
            entry_size = 0
            for i in range(min(20, file_count)):
                if epos + 48 > len(enc_data): break
                eoff = struct.unpack_from('<Q', enc_data, epos)[0]
                esize = struct.unpack_from('<Q', enc_data, epos+8)[0]
                ecsize = struct.unpack_from('<Q', enc_data, epos+16)[0]
                eflags = struct.unpack_from('<I', enc_data, epos+24)[0]
                if i < 5:
                    print(f'  [{i}] off={eoff}, sz={esize}, comp={ecsize}, flags={hex(eflags)}')
                epos += 48  # try 48 bytes per entry
            
            entry_size = epos // min(20, file_count)
            if entry_size > 0:
                print(f'Entry size: {entry_size} bytes')
            
            # Find Cody/May entry offsets
            print('\n--- Cody / May file data offsets ---')
            for path, entry_idx in dir_entries:
                if 'cody' in path.lower() and 'cody.uasset' in path.lower():
                    data_off = entry_idx * entry_size
                    if data_off < len(enc_data):
                        eoff = struct.unpack_from('<Q', enc_data, data_off)[0]
                        esize = struct.unpack_from('<Q', enc_data, data_off+8)[0]
                        print(f'  {path}: data_off={eoff}, size={esize}')
                elif 'may' in path.lower() and 'may.uasset' in path.lower():
                    data_off = entry_idx * entry_size
                    if data_off < len(enc_data):
                        eoff = struct.unpack_from('<Q', enc_data, data_off)[0]
                        esize = struct.unpack_from('<Q', enc_data, data_off+8)[0]
                        print(f'  {path}: data_off={eoff}, size={esize}')
