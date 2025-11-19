import os

APP_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(APP_DIR, 'resources.h'), 'r') as f:
    lines = f.read().split('\n')

lines_py = []
for line in lines:
    if line.startswith('#define '):
        parts = line[8:].strip().split(' ')
        lines_py.append(parts[0] + ' = ' + parts[1])

with open(os.path.join(APP_DIR, '..', 'src', 'resources.py'), 'w') as f:
    f.write('\n'.join(lines_py))
