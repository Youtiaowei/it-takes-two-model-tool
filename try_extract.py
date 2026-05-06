"""Try to extract with patched u4pak"""
import sys, os
sys.path.insert(0, '/home/youtiaowei/it-takes-two-model-tool')

# Apply v11 patch
from u4pak_v11_patch import patch_u4pak
patch_u4pak()

import u4pak

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')

# Try to read the index
with open(pak_path, 'rb') as f:
    try:
        records = u4pak.read_index(f)
        print(f'Success! Got {len(records)} records')
        for path, rec in sorted(records.items()):
            if 'cody' in path.lower() or 'may' in path.lower():
                if path.endswith('.uasset') or path.endswith('.uexp'):
                    if 'animation' not in path.lower() and 'audio' not in path.lower():
                        print(f'  {path}: offset={rec.offset}, size={rec.size}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
