"""
Extract specific files from UE4 v11 PAK (It Takes Two style)
using Directory Index which has plaintext filenames.
"""
import struct
import os
import sys
import zlib

PAK_FILE = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak"
OUTPUT_DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"

# Files we want to extract
TARGET_FILES = [
    "Nuts/Content/Characters/Cody/Cody.uasset",
    "Nuts/Content/Characters/Cody/Cody.uexp",
    "Nuts/Content/Characters/May/May.uasset",
    "Nuts/Content/Characters/May/May.uexp",
]

def find_footer(pakfile):
    """Find v11 PAK footer (magic at offset -204 from end)"""
    fsize = os.path.getsize(pakfile)
    with open(pakfile, 'rb') as f:
        f.seek(-300, 2)
        data = f.read(300)
    
    for i in range(len(data) - 4):
        magic = struct.unpack_from('<I', data, i)[0]
        if magic == 0x5A6F12E1:
            version = struct.unpack_from('<I', data, i+4)[0]
            idx_off = struct.unpack_from('<Q', data, i+8)[0]
            idx_sz = struct.unpack_from('<Q', data, i+16)[0]
            if 1 <= version <= 13 and 0 < idx_off < fsize and 0 < idx_sz < 200_000_000:
                print(f"  Footer found: version={version}, index_off={idx_off}, index_sz={idx_sz}")
                return version, idx_off, idx_sz, fsize - (300 - i)
    raise Exception("Footer not found")

def read_fstring(data, pos):
    """Read UE4 FString from bytes: int32 length + chars + null"""
    dlen = struct.unpack_from('<i', data, pos)[0]; pos += 4
    if dlen == 0:
        return '', pos
    abslen = abs(dlen)
    encoding = 'utf-16-le' if dlen < 0 else 'utf-8'
    s = data[pos:pos+abslen-1].decode(encoding, errors='replace')
    pos += abslen
    return s, pos

def extract_directory_index(pakfile, dir_off, dir_sz):
    """Parse the directory index from a v11 PAK"""
    with open(pakfile, 'rb') as f:
        f.seek(dir_off)
        raw = f.read(dir_sz)
    
    # Check compression (zlib)
    if len(raw) > 2 and raw[0] == 0x78 and raw[1] in (0x01, 0x9C, 0xDA):
        data = zlib.decompress(raw)
        print(f"  Directory index: decompressed {dir_sz} -> {len(data)} bytes")
    else:
        data = raw
        print(f"  Directory index: {len(data)} bytes (uncompressed)")
    
    pos = 0
    dir_count = struct.unpack_from('<i', data, pos)[0]; pos += 4
    print(f"  Directory count: {dir_count}")
    
    all_files = []
    for d in range(dir_count):
        dirname, pos = read_fstring(data, pos)
        
        entry_count = struct.unpack_from('<i', data, pos)[0]; pos += 4
        for e in range(entry_count):
            fname, pos = read_fstring(data, pos)
            entry_off = struct.unpack_from('<i', data, pos)[0]; pos += 4
            full_path = (dirname.rstrip('/') + '/' + fname).lstrip('/')
            all_files.append((full_path, entry_off))
    
    return all_files

# Add after directory parsing: read encoded entries to get file offsets
def parse_primary_index_structure(pakfile):
    """Parse primary index to find Directory Index offset"""
    version, idx_off, idx_sz, footer_pos = find_footer(pakfile)
    
    with open(pakfile, 'rb') as f:
        f.seek(idx_off)
        raw = f.read(idx_sz)
    
    pos = 0
    mount_point, pos = read_fstring(raw, pos)
    print(f"  Mount point: {mount_point}")
    
    file_count = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    print(f"  File count: {file_count}")
    
    path_hash_seed = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    print(f"  Hash seed: {path_hash_seed}")
    
    # HasPathHashIndex (int32)
    has_phi = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    phi_off = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    phi_sz = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    pos += 20  # SHA-1 hash
    
    # HasDirectoryIndex (int32)
    has_di = struct.unpack_from('<i', raw, pos)[0]; pos += 4
    dir_off = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    dir_sz = struct.unpack_from('<Q', raw, pos)[0]; pos += 8
    
    print(f"  PathHashIndex: offset={phi_off}, size={phi_sz}")
    print(f"  DirectoryIndex: offset={dir_off}, size={dir_sz}")
    print(f"  HasDirectoryIndex: {bool(has_di)}")
    
    if not has_di:
        print("  ERROR: No Directory Index in this PAK!")
        return None, None, None
    
    return dir_off, dir_sz, mount_point

def extract_file_data(pakfile, entry):
    """Extract a file's data from the PAK using its entry info"""
    # For v11, entries in the directory index point to encoded entries
    # The actual file data offset is in the encoded entry structure
    # This is complex - need to parse the FPakEntry struct
    pass

print("=" * 50)
print("UE4 v11 PAK File Extractor")
print("Target: It Takes Two")
print("=" * 50)

print(f"\nFile: {PAK_FILE}")
fsize = os.path.getsize(PAK_FILE)
print(f"Size: {fsize / (1024**3):.1f} GB")

# Step 1: Find footer
print("\n[1/4] Finding PAK footer...")
version, idx_off, idx_sz, footer_pos = find_footer(PAK_FILE)
print(f"  Version: {version}, Footer at: {footer_pos}")

# Step 2: Parse primary index to get directory index offset
print("\n[2/4] Parsing primary index...")
dir_off, dir_sz, mount_point = parse_primary_index_structure(PAK_FILE)
if not dir_off:
    sys.exit(1)

# Step 3: Extract directory index
print("\n[3/4] Extracting directory index...")
all_files = extract_directory_index(PAK_FILE, dir_off, dir_sz)
print(f"  Total files in index: {len(all_files)}")

# Step 4: Search for target files
print("\n[4/4] Searching for target files...")
found = []
for path, entry_off in all_files:
    for target in TARGET_FILES:
        if target.lower() in path.lower():
            found.append((path, entry_off))
            print(f"  ✅ FOUND: {path} (entry_offset={entry_off})")

if not found:
    print("\n  ❌ Target files not found")
    print("  Searching for any character files...")
    for path, entry_off in all_files:
        if 'character' in path.lower() or 'cody' in path.lower() or 'may' in path.lower():
            print(f"     {path}")
