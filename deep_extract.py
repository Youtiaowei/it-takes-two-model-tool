"""分析游戏 .pak 文件结构，尝试提取原始 .uasset 文件"""
import struct, zlib, os, sys

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')
output_dir = '/home/youtiaowei/it-takes-two-model-tool/extracted_chars'
os.makedirs(output_dir, exist_ok=True)

fsize = os.path.getsize(pak_path)

with open(pak_path, 'rb') as f:
    # Find proper footer by searching for magic at the end
    f.seek(-4096, 2)  # Search in the last 4KB
    end_data = f.read(4096)
    
    footer_pos = -1
    for i in range(len(end_data) - 4, -1, -4):
        magic = struct.unpack_from('<I', end_data, i)[0]
        if magic == 0x5A6F12E1:
            # Found magic, now check if the index offset makes sense
            fake_footer = end_data[i:]
            if len(fake_footer) >= 44:
                version = struct.unpack_from('<I', fake_footer, 4)[0]
                idx_off = struct.unpack_from('<Q', fake_footer, 8)[0]
                idx_sz = struct.unpack_from('<Q', fake_footer, 16)[0]
                if 1 <= version <= 13 and 0 < idx_off < fsize and idx_sz > 0 and idx_sz < idx_off:
                    footer_pos = fsize - len(end_data) + i
                    print(f"Found footer at pos {footer_pos}")
                    print(f"  version={version}, idx_off={idx_off:,}, idx_sz={idx_sz:,}")
                    break
    
    if footer_pos == -1:
        print("Could not find valid footer!")
        sys.exit(1)
    
    # Read the full footer (204 bytes for v11)
    f.seek(footer_pos)
    footer = f.read(204)
    
    # Parse footer
    pos = 0
    magic = struct.unpack_from('<I', footer, pos)[0]; pos += 4
    version = struct.unpack_from('<I', footer, pos)[0]; pos += 4
    idx_off = struct.unpack_from('<Q', footer, pos)[0]; pos += 8
    idx_sz = struct.unpack_from('<Q', footer, pos)[0]; pos += 8
    idx_hash = footer[pos:pos+20]; pos += 20
    encrypted = struct.unpack_from('<B', footer, pos)[0]; pos += 1
    frozen = struct.unpack_from('<B', footer, pos)[0]; pos += 1
    enc_key_guid = footer[pos:pos+16]; pos += 16
    
    # Compression methods (6 x 32-byte names)
    comp_methods = []
    for _ in range(6):
        name = footer[pos:pos+32].split(b'\x00')[0].decode('ascii', errors='replace')
        pos += 32
        comp_methods.append(name)
    print(f"  Compression methods: {comp_methods}")
    
    # After compression methods, there might be additional footer data
    remaining = len(footer) - pos
    print(f"  Remaining footer bytes: {remaining}")
    if remaining >= 8:
        # Read the compression block table
        # For v11, after the 6 compression method names, there might be:
        # block_count(uint32) + compression_block[]. Each block: flags(4) + compressed_size(4) + uncompressed_size(4) + extra(4)
        block_count = struct.unpack_from('<I', footer, pos)[0]; pos += 4
        print(f"  Compression blocks: {block_count}")
        
        if block_count > 0 and block_count < 100000:
            blocks = []
            for i in range(block_count):
                if pos + 16 > len(footer):
                    break
                bflags = struct.unpack_from('<I', footer, pos)[0]; pos += 4
                bcsize = struct.unpack_from('<I', footer, pos)[0]; pos += 4
                busize = struct.unpack_from('<I', footer, pos)[0]; pos += 4
                bextra = struct.unpack_from('<I', footer, pos)[0]; pos += 4
                blocks.append((bflags, bcsize, busize, bextra))
            
            if blocks:
                print(f"  First block: flags={hex(blocks[0][0])}")
                # The first block's compressed_size might be the offset into the file
                # where the index data starts
                print(f"  First block compressed_size={blocks[0][1]}, uncompressed_size={blocks[0][2]}")
    
    # Read the primary index
    print(f"\nReading primary index at {idx_off:,}...")
    f.seek(idx_off)
    raw_idx = f.read(min(idx_sz, 5000000))
    
    # Try to decompress
    try:
        if raw_idx[:2] in (b'\x78\x9c', b'\x78\xda', b'\x78\x01'):
            raw_idx = zlib.decompress(raw_idx)
            print(f"  Decompressed: {len(raw_idx)} bytes")
        else:
            print(f"  Raw index size: {len(raw_idx)} bytes")
            print(f"  First 32 bytes: {raw_idx[:32].hex()}")
    except:
        print(f"  Index not compressed, size: {len(raw_idx)} bytes")
    
    # Parse mount point
    pos = 0
    strlen = struct.unpack_from('<i', raw_idx, pos)[0]; pos += 4
    mount_raw = raw_idx[pos:pos+abs(strlen)-1]
    mount = mount_raw.decode('utf-8' if strlen > 0 else 'utf-16-le', errors='replace')
    pos += abs(strlen)
    print(f"  Mount: {mount}")
    
    # Skip file count, seed, path hash info, directory info...
    # Based on our earlier successful script, we know the structure
    # Let me just print the raw hex around relevant areas
    print(f"\n  Primary index structure:")
    print(f"    pos=0: mount_len={strlen}")
    print(f"    pos=4+strlen: {raw_idx[pos:pos+4].hex()} (file_count)")
    file_count = struct.unpack_from('<i', raw_idx, pos)[0]; pos += 4
    print(f"      -> file_count={file_count}")
    print(f"    pos={pos}: seed={raw_idx[pos:pos+8].hex()}")
    
    # Try to locate the "encoded entries" table which contains actual file data offsets
    # The structure after directory index info might be:
    # [HasEncodedEntries(int32)] [EncodedOffset(int64)] [EncodedSize(int64)]
    
    # Let me just check what's around pos+100
    print(f"\n  Hex dump around pos=100 from mount end:")
    start = min(pos + 40, len(raw_idx) - 100)
    for i in range(10):
        p = start + i*8
        if p + 8 <= len(raw_idx):
            val = struct.unpack_from('<Q', raw_idx, p)[0]
            print(f"    pos={p}: {val:20} (0x{val:016x})")
