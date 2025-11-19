import glob
"""
This script (heuristically) extracts the actually used Windows API constants
from the rather big constants scripts const.py, and saves them as "compiled"
version const_c.py, which is then used in the frozen app to save a few KB.
The script could definitely be optimized a lot, but it's not runtime code
and just needs about a second to run, so who cares.
"""

import winapp.const as c

total_code = ''

# Step 1: create a large string with all non-module python code used by the app.

for fn in glob.glob('**/*.py', recursive=True):
#    if fn.startswith('stuff\\') or (fn.startswith('plugins\\') and not fn.startswith('plugins\\paint')) or fn.startswith('dist\\') or fn.endswith('winapp\\const.py') or fn.endswith('const_c.py') :

    if fn.endswith('winapp\\const.py') or fn.endswith('winapp\\const_c.py') or fn.startswith('_'):
        continue

#    print(fn)
    with open(fn, 'r') as f:
        total_code += f.read() + ' '

# Step 2: check all constants from const.py if they appear as string somewhere in the code,
# and only save those in const_c.py that do.
# (we don't care about false positives, the goal here is to reduce the file/memory size in total)

with open('winapp\\const_c.py', 'w') as f:
    f.write('""" This is a "compiled" version containing only those constants that are actually used by the application """\n\n')

#    for k, v in c.__dict__.items():
#        if k.startswith('__'):
#            continue
#        if k in code:
#            f.write(f'{k} = "{v}"\n' if type(v) == str else f'{k} = {v}\n')

    d = c.__dict__
    for k in sorted(d.keys()):
        if k.startswith('__'):
            continue
        if k.startswith('VK_') or k in total_code:
            v = d[k]
            f.write(f'{k} = "{v}"\n' if type(v) == str else f'{k} = {v}\n')
