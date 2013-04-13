#!/usr/bin/python
'''
Converts the output of find_pictures.py to a JSON object.
'''

import fileinput

print 'var images = [';
print ','.join(fileinput.input())
print '];'
