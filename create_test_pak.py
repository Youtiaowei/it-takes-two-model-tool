"""
Last attempt: export vertex data from FBX, find matching pattern in .uexp, replace
"""
import struct, os, sys

# Step 1: Find the vertex buffer in .uexp
# Cody model: 69,924 vertices from game GLB
# We'll export known vertex positions from the new FBX and search for patterns

# But first - let's try the simplest approach: just create a mod .pak
# with the ORIGINAL unchanged files to verify the process works
print("Creating test mod .pak with original files...")

sys.path.insert(0, '/home/youtiaowei/it-takes-two-model-tool')
from u4pak import pack

# Create mount path entries
file_list = [
    ("../../../Nuts/Content/Characters/Cody/Cody.uasset",
     "/home/youtiaowei/it-takes-two-model-tool/extracted/Cody.uasset"),
    ("../../../Nuts/Content/Characters/Cody/Cody.uexp",
     "/home/youtiaowei/it-takes-two-model-tool/extracted/Cody.uexp"),
    ("../../../Nuts/Content/Characters/May/May.uasset",
     "/home/youtiaowei/it-takes-two-model-tool/extracted/May.uasset"),
    ("../../../Nuts/Content/Characters/May/May.uexp",
     "/home/youtiaowei/it-takes-two-model-tool/extracted/May.uexp"),
]

output_pak = "/home/youtiaowei/it-takes-two-model-tool/models/Model_Mod.pak"

try:
    pack(
        mount="../../../",
        entries=file_list,
        output=output_pak,
        version=8,
    )
    size = os.path.getsize(output_pak)
    print(f"✅ Pak created: {output_pak} ({size} bytes, {size/(1024*1024):.1f} MB)")
    print(f"   Contains original game files (no modifications)")
    print(f"   Place in: .../Nuts/Content/Paks/~mods/Model_Mod.pak")
except Exception as e:
    print(f"❌ Pack failed: {e}")
