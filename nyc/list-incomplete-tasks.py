#!/usr/bin/python
'''
Reads a detected-photos.txt file (the output of find_pictures.py) and a list of
files and outputs the ones that haven't been processed.

Can be fed into task-server.py to serve up remaining tasks.

Usage:
  ls images/*.jpg | ./list-incomplete-tasks.py detected-photos.txt | ./task-server.py
'''

import fileinput
import sys
import json
import os

completed = set()

assert len(sys.argv) == 2
for line in file(sys.argv[1]):
  d = json.loads(line)
  f = d['file']
  completed.add(os.path.basename(f))
sys.argv.pop()

for line in fileinput.input():
  f = line.strip()
  if os.path.basename(f) not in completed:
    print f
