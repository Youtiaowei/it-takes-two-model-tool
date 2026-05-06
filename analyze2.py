import struct, os

path = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak"
with open(path, 'rb') as f:
    f.seek(0, 2); size = f.tell()
    f.seek(size - 204); foot = f.read(44)
    idx_off = struct.unpack('<Q', foot[8:16])[0]
    idx_sz = struct.unpack('<Q', foot[16:24])[0]
    f.seek(idx_off)
    idx = f.read(idx_sz)

# Extract mount point
mount_len = struct.unpack('<I', idx[0:4])[0]
mount = idx[4:4+mount_len].split(b'\x00')[0].decode()

# The first few bytes of the index after mount point
# might give us info about directory structure
data = idx[4+mount_len:]
print(f"Mount: {mount}")
print(f"Index data size: {len(data)}")

# Check size of the first "file" - usually the mount directory entry
# After mount, the remaining data has compression block info
# Total blocks = len(data) / 16
total_blocks = len(data) // 16
print(f"Total 16-byte blocks: {total_blocks}")

# Read header for file count
with open(path, 'rb') as f:
    hdr = f.read(64)
q1 = struct.unpack('<Q', hdr[8:16])[0]
print(f"File count: {q1}")
print(f"Blocks per file: {total_blocks/q1:.1f}")
