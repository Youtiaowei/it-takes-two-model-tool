import struct

# Patch u4pak to handle Pak v11 format
# The main issue: footer at -204 instead of -44, and hashed filenames

def patch_u4pak():
    import u4pak
    
    # Monkey-patch read_index
    original_read_index = u4pak.read_index
    
    def patched_read_index(stream, check_integrity=False, ignore_magic=False, encoding='utf-8', force_version=None, ignore_null_checksums=False):
        import io, os
        
        size = os.fstat(stream.fileno()).st_size
        
        # V11: footer at -204 from end (not -44)
        stream.seek(-204, 2)
        footer_offset = stream.tell()
        footer = stream.read(44)
        magic, version, index_offset, index_size, index_sha1 = struct.unpack('<IIQQ20s', footer)
        
        if not ignore_magic and magic != 0x5A6F12E1:
            # Try original position
            stream.seek(-44, 2)
            footer_offset2 = stream.tell()
            footer2 = stream.read(44)
            magic2, version2, index_offset2, index_size2, _ = struct.unpack('<IIQQ20s', footer2)
            if magic2 == 0x5A6F12E1:
                return original_read_index(stream, check_integrity, ignore_magic, encoding, force_version, ignore_null_checksums)
            raise ValueError(f'illegal file magic: 0x{magic:08x}')
        
        if force_version is not None:
            version = force_version
        
        if index_offset + index_size > footer_offset:
            raise ValueError('illegal index offset/size')
        
        stream.seek(index_offset, 0)
        
        # Read mount point (path string)
        mount_len = struct.unpack('<I', stream.read(4))[0]
        mount_bytes = stream.read(mount_len)
        mount_point = mount_bytes.split(b'\x00')[0].decode(encoding, errors='replace')
        
        # Read remaining data as raw bytes
        remaining = stream.read(footer_offset - stream.tell())
        
        # Try to parse entries (format depends on version)
        # For v11, entries might be: path_hash(uint64) + entry data
        # But we don't know the hash function, so just return compression info
        
        pak = u4pak.Pak(version, index_offset, index_size, footer_offset, index_sha1, mount_point)
        
        # Read pak header for file count
        stream.seek(0)
        hdr = stream.read(64)
        file_count = struct.unpack('<Q', hdr[8:16])[0]
        block_count = struct.unpack('<Q', hdr[16:24])[0]
        
        print(f"[u4pak-v11] Mount: {mount_point}")
        print(f"[u4pak-v11] Files: {file_count}, Blocks: {block_count}")
        print(f"[u4pak-v11] Index: {index_size} bytes, Remaining: {len(remaining)} bytes")
        
        # The remaining index data contains the compression block table
        # Each entry is 16 bytes (4 x uint32): flags + comp_size + uncomp_size + ??? 
        # We can't list filenames but can show block info
        
        return pak
    
    u4pak.read_index = patched_read_index
    
    print("u4pak patched for v11 support!")

if __name__ == '__main__':
    patch_u4pak()
    
    import sys
    path = sys.argv[1]
    
    with open(path, 'rb') as f:
        pak = u4pak.read_index(f, ignore_magic=True)
        print(f"  Mount: {pak.mount_point}")
        print(f"  Records: {len(pak.records)} files")
