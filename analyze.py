import struct

path = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk7-WindowsNoEditor.pak"
with open(path, "rb") as f:
    f.seek(0, 2); size = f.tell()
    f.seek(size - 204); foot = f.read(44)
    idx_off = struct.unpack("<Q", foot[8:16])[0]
    idx_sz = struct.unpack("<Q", foot[16:24])[0]
    f.seek(idx_off); idx = f.read(idx_sz)

mount_len = struct.unpack("<I", idx[0:4])[0]
mount_name = idx[4:4+mount_len].split(b"\x00")[0].decode()
print(f"Mount: '{mount_name}'")
entries = idx[4+mount_len:]

for i in range(8):
    blk = entries[i*16:(i+1)*16]
    a, b, c, d = struct.unpack("<IIII", blk)
    print(f"Block {i}: [{a:>10d}] [{b:>10d}] [{c:>10d}] [{d:>10d}]")

with open(path, "rb") as f:
    hdr = f.read(64)
q1 = struct.unpack("<Q", hdr[8:16])[0]
q2 = struct.unpack("<Q", hdr[16:24])[0]
total_blocks = len(entries) // 16
print(f"\nHeader: file_count={q1}, block_count={q2}")
print(f"Blocks per file avg: {total_blocks/q1:.1f}")
print(f"Total blocks: {total_blocks}")
