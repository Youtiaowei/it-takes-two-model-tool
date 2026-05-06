"""
Create a mod .pak for It Takes Two using u4pak
Test: just package the original files unchanged
"""
import sys, os, json
sys.path.insert(0, '/home/youtiaowei/it-takes-two-model-tool')

from u4pak import pack, read_index
from pathlib import Path

EXTRACTED_DIR = "/home/youtiaowei/it-takes-two-model-tool/extracted"
OUTPUT_DIR = "/home/youtiaowei/it-takes-two-model-tool/mod_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Create the pak file list
# For a UE4 mod pak, files are mounted as:
# mount_point + relative_path
# The mount_point from the game is: ../../../ 
# And game content is under: Nuts/Content/

# For a mod .pak, the internal path should match the game's path
# e.g., ../../../Nuts/Content/Characters/Cody/Cody.uasset
mount_point = "../../../"
base_dir = os.path.join(EXTRACTED_DIR)

# Create a file list for u4pak
# u4pak expects: (mount_path, local_path) pairs
pak_entries = []

files_to_pack = [
    ("Nuts/Content/Characters/Cody/Cody.uasset", os.path.join(EXTRACTED_DIR, "Cody.uasset")),
    ("Nuts/Content/Characters/Cody/Cody.uexp", os.path.join(EXTRACTED_DIR, "Cody.uexp")),
    ("Nuts/Content/Characters/May/May.uasset", os.path.join(EXTRACTED_DIR, "May.uasset")),
    ("Nuts/Content/Characters/May/May.uexp", os.path.join(EXTRACTED_DIR, "May.uexp")),
]

for mount_path, local_path in files_to_pack:
    if os.path.exists(local_path):
        full_mount = mount_point + mount_path
        pak_entries.append((full_mount, local_path, 0))  # 0 = no compression
        print(f"  {full_mount} <- {local_path} ({os.path.getsize(local_path)} bytes)")
    else:
        print(f"  WARNING: {local_path} not found!")

# Step 2: Create the pak file
output_pak = os.path.join(OUTPUT_DIR, "model_mod.pak")
print(f"\nCreating {output_pak}...")

# Read the original pak to understand the format
original_pak = "/home/youtiaowei/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk2-WindowsNoEditor_0_P.pak"

# Use u4pak's pack function directly
# pack() takes: mount_point, entries, output_path, version, compression
from u4pak import pack as u4pack

# Prepare entries as (mount_path, local_path, compression_mode)
pack_entries = [(mount + local, local_fs, 0) for mount, local, comp in [(mount_point + mp, lp, 0) for mp, lp in [("Nuts/Content/Characters/Cody/Cody.uasset", os.path.join(EXTRACTED_DIR, "Cody.uasset")), ("Nuts/Content/Characters/Cody/Cody.uexp", os.path.join(EXTRACTED_DIR, "Cody.uexp")), ("Nuts/Content/Characters/May/May.uasset", os.path.join(EXTRACTED_DIR, "May.uasset")), ("Nuts/Content/Characters/May/May.uexp", os.path.join(EXTRACTED_DIR, "May.uexp"))]]]

print(f"\nAttempting to pack {len(pack_entries)} files...")
print(f"Output: {output_pak}")

# u4pak pack signature: pack(mount, entries, output, version=8, compression=0, align=0, encrypt=False, compress=None)
try:
    u4pack(
        mount=mount_point,
        entries=pack_entries,
        output=output_pak,
        version=8,  # UE4 standard, should work for loading
    )
    print(f"\n✅ Pak created: {output_pak} ({os.path.getsize(output_pak)} bytes)")
except Exception as e:
    print(f"\n❌ Pack failed: {e}")
    print("\nTrying with u4pak CLI...")
    import subprocess
    # Use CLI: python3 u4pak.py pack output.pak mount_point file1 file2 ...
    cmd = ["python3", "/home/youtiaowei/it-takes-two-model-tool/u4pak.py", "pack", output_pak, mount_point]
    for mp, lp in [("Nuts/Content/Characters/Cody/Cody.uasset", os.path.join(EXTRACTED_DIR, "Cody.uasset")), 
                   ("Nuts/Content/Characters/Cody/Cody.uexp", os.path.join(EXTRACTED_DIR, "Cody.uexp")),
                   ("Nuts/Content/Characters/May/May.uasset", os.path.join(EXTRACTED_DIR, "May.uasset")),
                   ("Nuts/Content/Characters/May/May.uexp", os.path.join(EXTRACTED_DIR, "May.uexp"))]:
        cmd.append(lp)
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(f"stdout: {result.stdout[:500]}")
    print(f"stderr: {result.stderr[:500]}")
    if result.returncode == 0:
        print(f"\n✅ Pak created via CLI!")
    else:
        print(f"\n❌ CLI failed: {result.stderr[:200]}")
