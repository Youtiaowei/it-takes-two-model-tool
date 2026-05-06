"""Try to extract with patched u4pak"""
import sys, os
sys.path.insert(0, '/home/youtiaowei/it-takes-two-model-tool')

from u4pak_v11_patch import patch_u4pak
patch_u4pak()

import u4pak

pak_path = os.path.expanduser('~/.steam/steam/steamapps/common/ItTakesTwo/Nuts/Content/Paks/pakchunk0-WindowsNoEditor.pak')

with open(pak_path, 'rb') as f:
    result = u4pak.read_index(f)
    
    records = result.records
    print(f'Total records: {len(records)}')
    print(f'First 5 records:')
    for i, rec in enumerate(records[:5]):
        print(f'  [{i}] name={rec.name}, offset={rec.offset}, size={rec.size}, comp_size={rec.compressed_size}')
    
    # Find Cody/May
    for rec in records:
        name = rec.name.lower()
        if ('cody' in name and (name.endswith('.uasset') or name.endswith('.uexp'))) or \
           ('/may/' in name and (name.endswith('.uasset') or name.endswith('.uexp'))):
            print(f'  => {rec.name}: offset={rec.offset}, size={rec.size}')
