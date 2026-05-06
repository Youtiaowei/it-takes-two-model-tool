#!/usr/bin/env python3
"""
UE4 PAK v11 reader - extracts files from It Takes Two PAK archives
Supports: PAK File Version 11 (PathHashIndex + Fnv64BugFix)
"""
import struct
import os
import sys
import zlib

PAK_MAGIC = 0x5A6F12E1
COMPRESSION_NONE = 0
COMPRESSION_ZLIB = 1
COMPRESSION_GZIP = 2
COMPRESSION_OODLE = 3
COMPRESSION_LZ4 = 4
COMPRESSION_ZSTD = 5

def read_fstring(data, offset):
    """Read UE4 FString (4-byte length prefix + UTF-8 data)"""
    strlen = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    if strlen == 0:
        return "", offset
    if strlen < 0:
        strlen = -strlen * 2  # UTF-16
        s = data[offset:offset+strlen-2].decode('utf-16-le', errors='replace')
        offset += strlen
    else:
        s = data[offset:offset+strlen-1].decode('utf-8', errors='replace')
        offset += strlen
    return s, offset

def parse_pak_footer(filepath):
    """Parse the PAK footer (FPakInfo)"""
    with open(filepath, 'rb') as f:
        f.seek(-204, 2)  # Standard footer size
        data = f.read(204)
    
    pos = 0
    magic = struct.unpack_from('<I', data, pos)[0]; pos += 4
    
    if magic != PAK_MAGIC:
        # Try other magic offsets (non-standard footer sizes)
        for try_offset in [200, 193, 192, 180, 176, 172, 168]:
            f.seek(-try_offset, 2)
            data2 = f.read(try_offset)
            magic2 = struct.unpack_from('<I', data2, try_offset-4)[0]
            if magic2 == PAK_MAGIC:
                print(f"  Found magic at offset -{try_offset}")
                data, pos = data2, try_offset - 4
                magic = magic2
                break
        else:
            print(f"  Magic check: found 0x{magic:08X}, expected 0x{PAK_MAGIC:08X}")
            f.seek(-256, 2)
            data = f.read(256)
            # Search for magic
            for i in range(len(data)-4, -1, -4):
                m = struct.unpack_from('<I', data, i)[0]
                if m == PAK_MAGIC:
                    pos = i
                    magic = m
                    print(f"  Found magic at offset {i} from end of 256-byte block")
                    break
    
    version = struct.unpack_from('<I', data, pos)[0]; pos += 4
    index_offset = struct.unpack_from('<Q', data, pos)[0]; pos += 8
    index_size = struct.unpack_from('<Q', data, pos)[0]; pos += 8
    index_hash = data[pos:pos+20]; pos += 20
    encrypted_index = struct.unpack_from('<B', data, pos)[0]; pos += 1
    index_is_frozen = struct.unpack_from('<B', data, pos)[0]; pos += 1
    enc_key_guid = data[pos:pos+16]; pos += 16
    
    # Compression methods (32-byte names x 6)
    comp_methods = []
    for _ in range(6):
        name = data[pos:pos+32].split(b'\x00')[0].decode('ascii', errors='replace')
        pos += 32
        comp_methods.append(name)
    
    info = {
        'magic': magic,
        'version': version,
        'index_offset': index_offset,
        'index_size': index_size,
        'encrypted_index': encrypted_index,
        'index_is_frozen': index_is_frozen,
    }
    return info

def parse_primary_index(filepath, index_offset, index_size):
    """Parse the Primary Index to get directory index offset"""
    with open(filepath, 'rb') as f:
        raw_index = read_decrypted_index(f, index_offset, index_size)
    
    pos = 0
    # Read MountPoint
    mount_point, pos = read_fstring(raw_index, pos)
    print(f"  MountPoint: {mount_point}")
    
    # Read FileCount
    file_count = struct.unpack_from('<i', raw_index, pos)[0]; pos += 4
    
    # Read PathHashSeed (8 bytes)
    path_hash_seed = struct.unpack_from('<Q', raw_index, pos)[0]; pos += 8
    
    # Read HasPathHashIndex
    has_path_hash = struct.unpack_from('<B', raw_index, pos)[0]; pos += 1
    if not has_path_hash:
        raise Exception("No path hash index")
    
    # Skip PathHashIndex info (offset + size + hash = 8+8+20 = 36 bytes)
    pos += 36
    
    # Read HasDirectoryIndex
    has_directory = struct.unpack_from('<B', raw_index, pos)[0]; pos += 1
    if not has_directory:
        raise Exception("No directory index")
    
    # Read DirectoryIndexOffset + DirectoryIndexSize + DirectoryIndexHash
    dir_offset = struct.unpack_from('<Q', raw_index, pos)[0]; pos += 8
    dir_size = struct.unpack_from('<Q', raw_index, pos)[0]; pos += 8
    dir_hash = raw_index[pos:pos+20]; pos += 20
    
    return mount_point, file_count, dir_offset, dir_size, raw_index[pos:]

def read_decrypted_index(f, offset, size):
    """Read and potentially decrypt the index"""
    f.seek(offset)
    data = f.read(size)
    # For now, assume unencrypted
    if size > 0 and data:
        # Try zlib decompression
        try:
            data = zlib.decompress(data)
        except:
            pass
    return data

def parse_directory_index(filepath, dir_offset, dir_size):
    """Parse the Directory Index to get all file paths and offsets"""
    with open(filepath, 'rb') as f:
        f.seek(dir_offset)
        raw_data = f.read(dir_size)
    
    # Try zlib decompression
    try:
        if raw_data[:2] in (b'\x78\xda', b'\x78\x01', b'\x78\x9c'):
            raw_data = zlib.decompress(raw_data)
    except:
        pass
    
    pos = 0
    dir_count = struct.unpack_from('<i', raw_data, pos)[0]; pos += 4
    print(f"  Directory count: {dir_count}")
    
    files = []
    for d in range(dir_count):
        dir_name, pos = read_fstring(raw_data, pos)
        file_count = struct.unpack_from('<i', raw_data, pos)[0]; pos += 4
        
        for _ in range(file_count):
            file_name, pos = read_fstring(raw_data, pos)
            entry_offset = struct.unpack_from('<i', raw_data, pos)[0]; pos += 4
            
            if entry_offset == -2147483648:  # int.MinValue
                continue
            
            path = dir_name.rstrip('/') + '/' + file_name
            files.append((path, entry_offset))
    
    return files

def extract_file(filepath, mount_point, data_offset, output_dir):
    """Extract a single file from the PAK"""
    # For now, just note what we found
    pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_pak.py <pakfile> [output_dir]")
        sys.exit(1)
    
    pakfile = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "extracted"
    
    print(f"Parsing: {os.path.basename(pakfile)}")
    print(f"  Size: {os.path.getsize(pakfile) / 1e9:.2f} GB")
    
    # Parse footer
    info = parse_pak_footer(pakfile)
    print(f"  Version: {info['version']}")
    print(f"  Index offset: {info['index_offset']}")
    print(f"  Index size: {info['index_size']}")
    print(f"  Encrypted: {info['encrypted_index']}")
    print(f"  Frozen: {info['index_is_frozen']}")
    
    if info['version'] < 10:
        print("  Legacy index, trying to list with standard parser...")
        return
    
    # Parse primary index
    try:
        mount_point, file_count, dir_offset, dir_size, remaining = parse_primary_index(
            pakfile, info['index_offset'], info['index_size']
        )
        print(f"  Total files: {file_count}")
        print(f"  Directory index offset: {dir_offset}")
        print(f"  Directory index size: {dir_size}")
    except Exception as e:
        print(f"  Error parsing primary index: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Parse directory index
    try:
        files = parse_directory_index(pakfile, dir_offset, dir_size)
        print(f"  Files in directory index: {len(files)}")
        
        # Show first 30 files
        for path, offset in files[:30]:
            print(f"    {path} (offset: {offset})")
        
        # Search for Cody and May
        cody_files = [(p, o) for p, o in files if 'cody' in p.lower()]
        may_files = [(p, o) for p, o in files if 'may' in p.lower()]
        
        print(f"\n  🎯 Cody files: {len(cody_files)}")
        for p, o in cody_files[:20]:
            print(f"    {p}")
        
        print(f"\n  🎯 May files: {len(may_files)}")
        for p, o in may_files[:20]:
            print(f"    {p}")
            
    except Exception as e:
        print(f"  Error parsing directory index: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
