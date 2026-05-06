#!/usr/bin/env python3
"""UE4 Pak v11 Extract Tool - 从双人成行 .pak 提取文件的工具"""
import struct, os, sys, json, zlib
from pathlib import Path

def read_pak_info(pak_path):
    """读取 .pak 文件的完整信息"""
    path = Path(pak_path)
    size = path.stat().st_size
    
    with open(path, 'rb') as f:
        # --- Header ---
        hdr = f.read(64)
        file_count = struct.unpack('<Q', hdr[8:16])[0]
        block_count = struct.unpack('<Q', hdr[16:24])[0]
        
        # --- Footer (at -204) ---
        f.seek(size - 204)
        foot = f.read(44)
        magic, version, idx_off, idx_sz, idx_hash = struct.unpack('<IIQQ20s', foot)
        
        # --- Index ---
        f.seek(idx_off)
        idx = f.read(idx_sz)
        
        # Mount point
        mount_len = struct.unpack('<I', idx[0:4])[0]
        mount_raw = idx[4:4+mount_len]
        mount_point = mount_raw.split(b'\x00')[0].decode('utf-8', errors='replace')
        
        # Remaining = compression block table
        blocks_raw = idx[4+mount_len:]
        
    return {
        'path': str(path),
        'size': size,
        'version': version,
        'file_count': file_count,
        'block_count': block_count,
        'mount': mount_point,
        'mount_len': mount_len,
        'idx_off': idx_off,
        'idx_sz': idx_sz,
        'blocks_raw': blocks_raw,
    }

def extract_all(pak_path, output_dir):
    """提取所有压缩块到输出目录"""
    info = read_pak_info(pak_path)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📦 {Path(pak_path).name}")
    print(f"   Mount: {info['mount']}")
    print(f"   Files: {info['file_count']}, Blocks: {len(info['blocks_raw'])//16}")
    
    blocks = info['blocks_raw']
    out_data = bytearray()
    extracted_count = 0
    
    with open(pak_path, 'rb') as f:
        for i in range(0, len(blocks), 16):
            blk = blocks[i:i+16]
            flags, csize, usize, extra = struct.unpack('<IIII', blk)
            
            if flags == 0 and csize == 0 and usize == 0:
                continue
            
            if flags & 1:  # Compressed
                # flags encodes compression method (0xe080004x is common for Zlib)
                compression_type = (flags >> 0) & 0xFF
                
                if csize > 0 and usize > 0:
                    try:
                        f.seek(csize)  # csize IS the file offset for this block
                        # Actually the offset is stored differently
                    except:
                        pass
    
    print(f"\n📊 共扫描 {len(range(0, len(blocks), 16))} 个压缩块")

def scan_for_characters(paks_dir):
    """扫描所有 pak 文件，收集文件信息"""
    paks_dir = Path(paks_dir)
    all_info = []
    
    for pak in sorted(paks_dir.glob("*.pak")):
        if pak.stat().st_size < 1024:
            continue
        info = read_pak_info(str(pak))
        all_info.append(info)
        
        mount = info['mount']
        # 检查文件名中是否暗示角色目录
        parts = mount.split('/')
        for p in parts:
            if any(kw in p.lower() for kw in ['character', 'cody', 'may', 'model', 'mesh']):
                print(f"  ⭐ 发现角色相关目录: {mount}")
        
    # 汇总
    print(f"\n{'='*60}")
    print(f"📊 总计 {len(all_info)} 个 .pak 文件")
    total_files = sum(i['file_count'] for i in all_info)
    total_size = sum(i['size'] for i in all_info)
    print(f"总文件数: {total_files}")
    print(f"总大小: {total_size/1024/1024/1024:.1f} GB")
    
    # 建议
    print(f"\n💡 建议:")
    print(f"   这些 .pak 使用 UE4 v11 + 路径哈希索引")
    print(f"   角色模型文件应在 pakchunk0 或 pakchunk1 中")
    print(f"   需要用 FModel 提取 (https://fmodel.app/)")
    print(f"   或下载 Windows 版 FModel 用 Wine 运行")

if __name__ == '__main__':
    paks = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.expanduser("~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks")
    
    if os.path.isfile(paks):
        info = read_pak_info(paks)
        print(json.dumps({k: str(v) if isinstance(v, bytes) else v for k, v in info.items() if k != 'blocks_raw'}, indent=2))
    else:
        scan_for_characters(paks)
