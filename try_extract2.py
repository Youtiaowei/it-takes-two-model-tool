"""Try to extract with patched u4pak - debug"""
import sys, os
sys.path.insert(0, '/home/youtiaowei/it-takes-two-model-tool')

from u4pak_v11_patch import patch_u4pak
patch_u4pak()

import u4pak

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')

with open(pak_path, 'rb') as f:
    result = u4pak.read_index(f)
    print(f'Result type: {type(result)}')
    attrs = [x for x in dir(result) if not x.startswith('_')]
    print(f'Result dir: {attrs}')
    
    # Try to iterate
    if hasattr(result, 'items'):
        for k,v in result.items():
            print(f'  {k}: {v}')
    elif hasattr(result, 'records'):
        for k,v in result.records.items():
            if 'cody' in k.lower() and (k.endswith('.uasset') or k.endswith('.uexp')):
                print(f'  {k}: offset={v.offset}, size={v.size}')
    elif hasattr(result, '__iter__'):
        for item in result:
            if hasattr(item, 'name') and 'cody' in item.name.lower():
                print(f'  {item.name}')
    else:
        # Try to access properties
        for attr in ['mount_point', 'file_count', 'files', 'entries']:
            if hasattr(result, attr):
                val = getattr(result, attr)
                print(f'  {attr}: {val}')
