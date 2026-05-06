"""Create test mod .pak with original game files"""
import os, sys
sys.path.insert(0, '/home/youtiaowei/it-takes-two-model-tool')
from u4pak import pack

output_pak = "/home/youtiaowei/it-takes-two-model-tool/models/Model_Mod.pak"

# Files to pack: list of their paths on disk
# u4pak uses the mount_point for all files
files = [
    "/home/youtiaowei/it-takes-two-model-tool/extracted/Cody.uasset",
    "/home/youtiaowei/it-takes-two-model-tool/extracted/Cody.uexp",
    "/home/youtiaowei/it-takes-two-model-tool/extracted/May.uasset",
    "/home/youtiaowei/it-takes-two-model-tool/extracted/May.uexp",
]

# Mount point for the game is ../../../ which maps to Nuts/Content/
mount_point = "../../../"

with open(output_pak, 'wb') as f:
    pack(
        stream=f,
        files_or_dirs=files,
        mount_point=mount_point,
        version=3,  # v3 is widely compatible
    )

size = os.path.getsize(output_pak)
print(f"✅ Pak created: {output_pak}")
print(f"   Size: {size} bytes ({size/(1024*1024):.1f} MB)")
print(f"   Files: {len(files)}")
print(f"   Mount: {mount_point}")
print(f"")
print(f"📂 Place this file in:")
print(f"   Steam/steamapps/common/It Takes Two/Nuts/Content/Paks/~mods/")
print(f"")
print(f"⚠️ Note: This mod contains the ORIGINAL game files (no model changes).")
print(f"   It's a test to verify the mod loading system works.")
