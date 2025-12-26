import glob
"""
This script (heuristically) extracts the actually used Windows API functions
from the rather big script dlls.py, and saves them as "compiled"
version dlls_c.py, which is then used in the frozen app to save a few KB of RAM.
"""

import winapp.dlls as d

exported_functions = [dll + '.' + f for dll in d.__dlls__ for f in dir(getattr(d, dll)) if f[0] != '_']

total_code = ''

########################################
# Step 1: create a large string with all non-module python code used by the app.
########################################

for fn in glob.glob('**/*.py', recursive=True):
    if fn.endswith('winapp\\dlls.py') or fn.endswith('winapp\\dlls_c.py') or fn.startswith('_'):
        continue
    with open(fn, 'r') as f:
        total_code += f.read() + ' '

########################################
#
########################################
dlls_used = {}
for dll in d.__dlls__:
    dlls_used[dll] = False
lines_used = []

########################################
# Go through all lines in dlls.py
########################################
with open('winapp\\dlls.py', 'r') as f:
    lines = f.read().splitlines()

for line in lines:
    if line == '' or line.startswith('#'):
        continue
    if '.argtypes' in line:
        line = line.lstrip()
        func = line[:line.index('.argtypes')]
        if func in exported_functions and func + '(' in total_code:
            dlls_used[line.split('.')[0]] = True
            lines_used.append(line)
    elif '.restype' in line:
        line = line.lstrip()
        func = line[:line.index('.restype')]
        if func in exported_functions and func + '(' in total_code:
            dlls_used[line.split('.')[0]] = True
            lines_used.append(line)
    elif ' = ' in line:
        line = line.lstrip()
        func = line[:line.index(' = ')]
        if func in exported_functions and func + '(' in total_code:
            dlls_used[line.split('.')[0]] = True
            lines_used.append(line)

########################################
#
########################################
with open('winapp\\dlls_c.py', 'w') as f:
    f.write('""" This is a "compiled" version containing only those dlls and functions that are actually used by the application """\n\n')
    f.write('from ctypes.wintypes import *\n')
    f.write('from .types import *\n\n')
    for dll, flag in dlls_used.items():
        if flag:
            f.write(f'{dll} = ctypes.windll.{dll}\n')
    f.write('\n')
    for line in lines_used:
        f.write(line + '\n')
