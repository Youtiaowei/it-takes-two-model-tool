"""Extract It Takes Two pak file index using path hash approach"""
import struct, os, sys

PAKS_DIR = os.path.expanduser(
    "~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks")

def read_pak_index(pak_path):
    """Read a .pak file's index (mount point + entries)"""
    size = os.path.getsize(pak_path)
    with open(pak_path, 'rb') as f:
        # Read footer
        f.seek(size - 204)
        foot = f.read(44)
        magic = struct.unpack('<I', foot[0:4])[0]
        ver = struct.unpack('<I', foot[4:8])[0]
        idx_off = struct.unpack('<Q', foot[8:16])[0]
        idx_sz = struct.unpack('<Q', foot[16:24])[0]
        
        # Read index
        f.seek(idx_off)
        idx = f.read(idx_sz)
        
        # Read header
        f.seek(0)
        hdr = f.read(64)
    
    file_count = struct.unpack('<Q', hdr[8:16])[0]
    block_count = struct.unpack('<Q', hdr[16:24])[0]
    
    # Parse mount point
    mount_len = struct.unpack('<I', idx[0:4])[0]
    mount_name = idx[4:4+mount_len].split(b'\x00')[0].decode('utf-8', errors='replace')
    
    return {
        'path': pak_path,
        'size': size,
        'version': ver,
        'file_count': file_count,
        'block_count': block_count,
        'mount': mount_name,
        'index_size': idx_sz,
    }

def main():
    results = []
    for pak in sorted(os.listdir(PAKS_DIR)):
        if not pak.endswith('.pak'):
            continue
        pak_path = os.path.join(PAKS_DIR, pak)
        if os.path.getsize(pak_path) < 1024:
            continue
        info = read_pak_index(pak_path)
        results.append(info)
        print(f"📦 {pak:45s} | {info['size']/1024/1024/1024:>5.1f} GB | "
              f"v{info['version']} | {info['file_count']:>6d} files | "
              f"mount: {info['mount'][:50]}")
    
    print(f"\n{'='*70}")
    print(f"总计 {len(results)} 个 .pak 文件")
    
    total_files = sum(r['file_count'] for r in results)
    total_size = sum(r['size'] for r in results)
    print(f"总文件数: {total_files}")
    print(f"总大小: {total_size/1024/1024/1024:.1f} GB")
    print(f"\n💡 提示: 这些 .pak 使用 UE4 Pak v11 格式 + 路径哈希索引")
    print(f"   文件名不直接存储在索引中")
    print(f"   需要使用 FModel/UEViewer 等专业工具提取")

if __name__ == '__main__':
    main()
