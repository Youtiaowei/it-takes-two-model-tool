#!/usr/bin/env python3
"""UE4 Pak v11 文件索引解析器 - 直接从索引二进制流解析文件名"""
import struct, sys, os, zlib
from pathlib import Path

PAK_MAGIC = 0x5A6F12E1

def find_footer(path, scan_size=65536):
    """在文件尾部查找 Pak Footer"""
    size = os.path.getsize(path)
    scan = min(size, scan_size)
    with open(path, 'rb') as f:
        f.seek(size - scan)
        tail = f.read()
    for i in range(len(tail) - 4, -1, -1):
        magic = struct.unpack('<I', tail[i:i+4])[0]
        if magic != PAK_MAGIC:
            continue
        if i + 44 > len(tail):
            continue
        ver = struct.unpack('<I', tail[i+4:i+8])[0]
        idx_off = struct.unpack('<Q', tail[i+8:i+16])[0]
        idx_sz = struct.unpack('<Q', tail[i+16:i+24])[0]
        if 0 < idx_sz < 50*1024*1024 and 0 < idx_off < size:
            return ver, idx_off, idx_sz
    return None

def parse_index_entries(idx_data):
    """
    UE4 Pak v8+ index entry format (from engine source):
    - int32: name length (including null)
    - byte[name_length]: name (null-terminated UTF-8)
    - int64: offset in pak
    - int64: compressed size (if not compressed, == uncompressed)
    - int64: uncompressed size
    - int32: compression method (0=None, 1=Zlib, 2=Gzip, 3=Oodle, 4=Zstd)
    - byte[20]: SHA1 hash
    """
    entries = []
    pos = 0
    while pos + 8 <= len(idx_data):
        name_len = struct.unpack('<I', idx_data[pos:pos+4])[0]
        pos += 4
        
        if name_len <= 0 or name_len > 1024:
            break
        if pos + name_len > len(idx_data):
            break
        
        raw_name = idx_data[pos:pos+name_len]
        pos += name_len
        
        # Name may have null padding
        name = raw_name.split(b'\x00')[0].decode('utf-8', errors='replace')
        
        if pos + 48 > len(idx_data):
            break
        
        # int64 offset
        file_off = struct.unpack('<Q', idx_data[pos:pos+8])[0]
        pos += 8
        
        # int64 compressed size
        comp_size = struct.unpack('<Q', idx_data[pos:pos+8])[0]
        pos += 8
        
        # int64 uncompressed size
        uncomp_size = struct.unpack('<Q', idx_data[pos:pos+8])[0]
        pos += 8
        
        # int32 compression method
        comp_method = struct.unpack('<I', idx_data[pos:pos+4])[0]
        pos += 4
        
        # byte[20] hash
        pos += 20
        
        entries.append((name, file_off, comp_size, uncomp_size, comp_method))
    
    return entries

def process_pak(pak_path):
    path = Path(pak_path)
    size = path.stat().st_size
    
    print(f"\n{'='*70}")
    print(f"📦 {path.name} ({size/1024/1024/1024:.1f} GB)")
    
    footer = find_footer(str(path))
    if not footer:
        print("❌ 未找到 Pak Footer")
        return []
    
    ver, idx_off, idx_sz = footer
    print(f"  版本: v{ver}, 索引偏移: {idx_off}, 索引大小: {idx_sz/1024:.0f} KB")
    
    with open(path, 'rb') as f:
        f.seek(idx_off)
        idx_raw = f.read(idx_sz)
    
    # Check for compression at start of index
    if idx_raw[:2] == b'\x78\x9c' or idx_raw[:2] == b'\x78\x01':
        idx_data = zlib.decompress(idx_raw)
        print(f"  ⚡ 索引已 zlib 解压: {len(idx_data)} bytes ({len(idx_raw)} > {len(idx_data)})")
    elif idx_raw[0] in (0x01, 0x02, 0x0A, 0x00):
        # No compression - try direct parse
        idx_data = idx_raw
        print(f"  索引未压缩，直接解析 ({len(idx_data)} bytes)")
    else:
        # Try skipping first byte
        try:
            idx_data = zlib.decompress(idx_raw[1:])
            print(f"  ⚡ 跳过1字节后 zlib 解压: {len(idx_data)} bytes")
        except:
            try:
                idx_data = zlib.decompress(idx_raw[2:])
                print(f"  ⚡ 跳过2字节后 zlib 解压: {len(idx_data)} bytes")
            except:
                idx_data = idx_raw
                print(f"  ⚡ 原始索引 ({len(idx_data)} bytes)")
    
    entries = parse_index_entries(idx_data)
    print(f"  文件总数: {len(entries):,}")
    
    # Filter for character models
    characters = {
        '科迪 (Cody)': ['cody', 'sk_cody'],
        '小梅 (May)': ['may', 'sk_may'],
        '罗斯 (Rose)': ['rose', 'sk_rose'],
        '哈基姆 (Hakim)': ['hakim', 'sk_hakim'],
        '布偶 (Cutie)': ['cutie', 'sk_cutie'],
    }
    
    results = {}
    for char_name, keywords in characters.items():
        char_files = []
        for name, off, cs, us, cm in entries:
            name_lower = name.lower()
            if any(kw in name_lower for kw in keywords):
                char_files.append((name, us))
        if char_files:
            results[char_name] = char_files
            total = sum(f[1] for f in char_files)
            print(f"\n  🎮 {char_name}: {len(char_files)} 个 ({total/1024/1024:.0f} MB)")
    
    return entries

def main():
    pak_dir = sys.argv[1] if len(sys.argv) > 1 else \
              os.path.expanduser("~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks")
    
    path = Path(pak_dir)
    if path.is_file():
        process_pak(str(path))
    else:
        all_entries = []
        for pf in sorted(path.glob("*.pak")):
            if pf.stat().st_size > 10*1024*1024:  # Only process > 10MB files
                entries = process_pak(str(pf))
                all_entries.extend(entries)
        
        print(f"\n\n{'='*70}")
        print(f"📊 所有角色模型汇总")
        print(f"{'='*70}")
        
        # Search all entries
        char_map = {
            '科迪 (Cody)': ['cody', 'sk_cody'],
            '小梅 (May)': ['may', 'sk_may'],
        }
        
        for char_name, keywords in char_map.items():
            char_files = [(n, s) for n, o, cs, us, cm in all_entries 
                          if any(kw in n.lower() for kw in keywords)]
            char_files.sort(key=lambda x: -x[1])
            
            print(f"\n🎮 {char_name}: {len(char_files)} 个文件")
            
            # .uasset skeleton mesh files (actual model files)
            meshes = [(n, s) for n, s in char_files if n.endswith('.uasset') and not any(
                x in n.lower() for x in ['phys', 'anim', 'icon', 'thumb', 'sound', 'texture', 'shader'])]
            
            if meshes:
                print(f"\n  🦴 角色网格体/模型:")
                for name, size in meshes[:15]:
                    print(f"    {size/1024/1024:>6.1f} MB  {name[:100]}")

if __name__ == "__main__":
    main()
