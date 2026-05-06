#!/usr/bin/env python3
"""Parse UE4 Pak v11 (PAKFS) index - dump hash entries"""
import struct, os, sys

def parse_pak(path):
    size = os.path.getsize(path)
    
    with open(path, 'rb') as f:
        # Header
        hdr = f.read(64)
        file_count = struct.unpack('<Q', hdr[8:16])[0]
        
        # Footer at -204
        f.seek(size - 204)
        foot = f.read(44)
        idx_off, idx_sz = struct.unpack('<QQ', foot[8:24])
        
        # Read index
        f.seek(idx_off)
        idx = f.read(idx_sz)
        
        # Mount point
        mount_len = struct.unpack('<I', idx[0:4])[0]
        mount = idx[4:4+mount_len].split(b'\x00')[0].decode()
        
        data = idx[4+mount_len:]
        
        # PAKFS v2 format:
        # The index contains directory tree entries + file entries
        # Each entry has:
        #   uint64 path_hash
        #   var-length children info
        # Then at the end: compression blocks
        
        # Let's just dump all uint64 values and look for patterns
        print(f"File: {os.path.basename(path)}")
        print(f"Mount: {mount}")
        print(f"Files: {file_count}")
        print(f"Index size: {len(data)} bytes\n")
        
        # Try to find the character model paths by scanning strings
        # Since filenames aren't stored, we need a different approach
        # Let's dump all hashes to search online later
        print("Dumping all path hashes...")
        
        pos = 0
        entry_num = 0
        hashes = []
        
        while pos + 8 <= len(data) and entry_num < file_count:
            path_hash = struct.unpack('<Q', data[pos:pos+8])[0]
            hashes.append(path_hash)
            
            # Skip the entry - determine its size
            # PAKFS entry: hash(8) + flags(1) + ... other fields
            # We need to figure out the entry size from flags
            pos += 8
            entry_num += 1
            
            if entry_num % 100 == 0 or entry_num < 10:
                print(f"  Entry {entry_num}: hash=0x{path_hash:016X} at pos={pos-8}")
        
        print(f"\nScanned {entry_num} entries, {len(hashes)} hashes collected")
        print(f"Position: {pos}/{len(data)}")

if __name__ == '__main__':
    pak_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks")
    
    if os.path.isdir(pak_dir):
        for p in sorted(os.listdir(pak_dir)):
            if p.endswith('.pak') and 'pakchunk7' in p:
                parse_pak(os.path.join(pak_dir, p))
    else:
        parse_pak(pak_dir)
