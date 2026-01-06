import glob
"""
This script (heuristically) extracts the actually used Windows API constants
from the rather big constants scripts const.py, and saves them as "compiled"
version const_c.py, which is then used in the frozen app to save a few KB.
The script could definitely be optimized a lot, but it's not runtime code
and just needs about a second to run, so who cares.
"""

import winapp.const as c

WHITE_LIST = [
    'CLSID_Desktop',
    'CLSID_Documents',
    'CLSID_Downloads',
    'CLSID_Libraries',
    'CLSID_Music',
    'CLSID_Network',
    'CLSID_RecycleBin',
    'CLSID_Start',
    'CLSID_ThisPC',
    'CLSID_UserProfile',
    'CLSID_Videos',
]

total_code = ''

# Step 1: create a large string with all non-module python code used by the app.

for fn in glob.glob('**/*.py', recursive=True):
    if fn.endswith('winapp\\const.py') or fn.endswith('winapp\\const_c.py') or fn.startswith('_'):
        continue
    with open(fn, 'r') as f:
        total_code += f.read() + ' '

# Step 2: check all constants from const.py if they appear as string somewhere in the code,
# and only save those in const_c.py that do.
# (we don't care about false positives, the goal here is to reduce the file/memory size in total)

with open('winapp\\const_c.py', 'w') as f:
    f.write('""" This is a "compiled" version containing only those constants that are actually used by the application """\n\n')
    d = c.__dict__
    for k in sorted(d.keys()):
        if k.startswith('__'):
            continue
        if k in total_code or k in WHITE_LIST:
            v = d[k]
            f.write(f'{k} = "{v}"\n' if type(v) == str else f'{k} = {v}\n')
