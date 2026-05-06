#!/usr/bin/env python3
"""
Extract files from UE4 Pak v11 (PAKFS) using known internal paths.
Based on understanding of PAKFS hash-based index.
"""
import struct, os, sys, mmap, hashlib

PAKS_DIR = os.path.expanduser(
    "~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks")

# Known character model paths (from AngelScript source files):
# Format: mount_point + internal_path
MOUNT_POINT = "../../../"

CHARACTER_PATHS = {
    "cody_uasset": "Nuts/Content/Characters/Cody/Cody.uasset",
    "cody_uexp":   "Nuts/Content/Characters/Cody/Cody.uexp",
    "cody_ubulk":  "Nuts/Content/Characters/Cody/Cody.ubulk",
    "may_uasset":  "Nuts/Content/Characters/May/May.uasset",
    "may_uexp":    "Nuts/Content/Characters/May/May.uexp",
    "may_ubulk":   "Nuts/Content/Characters/May/May.ubulk",
}

def fnv1a_64(data: bytes) -> int:
    """FNV-1a 64-bit hash (used by UE4 for path hashing)"""
    hash_val = 0xCBF29CE484222325
    for byte in data:
        hash_val ^= byte
        hash_val = (hash_val * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return hash_val

def compute_hashes():
    """Compute FNV-1a 64-bit hashes for all known paths"""
    print("="*60)
    print("UE4 Path Hash Computation")
    print("="*60)
    
    # Try different path formats
    for name, path in CHARACTER_PATHS.items():
        print(f"\n--- {name} ---")
        # Various UE4 hash formats
        variants = [
            path,                                    # Nuts/Content/...
            path.lower(),                            # nuts/content/...
            path.replace("/", "\\"),                 # Nuts\Content\...
            path.lower().replace("/", "\\"),         # nuts\content\...
            "../" + path,                            # ../Nuts/Content/...
            "../../" + path,                         # ../../Nuts/Content/...
            "../../.." + path,                       # ../../../Nuts/Content/...
            MOUNT_POINT + path,                      # ../../../Nuts/Content/...
            "/" + path,                              # /Nuts/Content/...
            "/Game" + path.split("Content")[1] if "Content" in path else path, # /Game/Characters/...
        ]
        
        for v in variants:
            h = fnv1a_64(v.encode('utf-8'))
            print(f"  \"{v}\"")
            print(f"    → 0x{h:016X}")

def parse_pak_index(pak_path):
    """Parse v11 PAKFS index and return {hash: (offset, comp_size, uncomp_size, method)}"""
    size = os.path.getsize(pak_path)
    entries = {}
    
    with open(pak_path, 'rb') as f:
        # Read header for file count
        f.seek(0)
        hdr = f.read(64)
        file_count = struct.unpack('<Q', hdr[8:16])[0]
        
        # Read footer
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
        
        # DEBUG: dump hex of first 100 bytes
        print(f"\nFirst 200 bytes of index data for {os.path.basename(pak_path)}:")
        hex_str = ' '.join(f'{b:02X}' for b in data[:200])
        for i in range(0, len(hex_str), 80):
            print(hex_str[i:i+80])
        
        # Parse PAKFS entries
        # The format is complex - let's try different approaches
        pos = 0
        entry_num = 0
        found_hashes = {}
        
        while pos + 8 <= len(data) and entry_num < file_count:
            # Read path hash (uint64)
            path_hash = struct.unpack('<Q', data[pos:pos+8])[0]
            pos += 8
            
            # Read entry info - the format after hash varies
            # In UE5 PAKFS v2:
            # uint64 hash
            # varint encoding for the rest...
            # Let's try: read the first byte after hash as flags
            if pos >= len(data):
                break
            
            flags = data[pos]
            pos += 1
            
            # Based on flags, the entry could be:
            # - Directory entry (no file data)
            # - File entry with compression blocks
            
            if flags & 0x80:  # It's a file entry?
                pass
            
            entry_num += 1
            if entry_num > file_count:
                break
        
        print(f"\nScanned {entry_num} entries from {os.path.basename(pak_path)}")
    
    return entries

def main():
    compute_hashes()
    
    print("\n\n" + "="*60)
    print("PAK File Index Analysis")
    print("="*60)
    
    # Analyze pakchunk0 (12.8 GB - likely has character models)
    for pak_name in ["pakchunk0-WindowsNoEditor.pak"]:  # Start with one
        pak_path = os.path.join(PAKS_DIR, pak_name)
        if os.path.exists(pak_path):
            parse_pak_index(pak_path)
            break  # Just analyze one for now

if __name__ == "__main__":
    main()
