#!/usr/bin/env python
'''Use the transcriptions of backing images to group letters.

The output of this is ocr/images/by-letter/[a-zA-Z0-9,.]/*.png
'''

import csv
import errno
import shutil
import sys
import os


# From http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else: raise


def escape_letter(char):
    # The OS X file system is case insensitive.
    # This makes sure that 'a' and 'A' get mapped to different directories, and
    # that the file name is valid (i.e. doesn't have a slash in it).
    safe_char = char.replace(r'[^a-zA-Z0-9.,"\'\[\]\(\)]', '')
    return str(ord(char)) + safe_char


for row in csv.DictReader(open('ocr/transcribe/output.csv')):
    photo_id = row['photo_id']
    num_cols = row['num_cols']
    num_rows = row['num_rows']
    transcription = row['transcription']

    for j, line in enumerate(transcription.split('\n')):
        for i, char in enumerate(line):
            if char == '\r' or char == '\n' or char == ' ': continue

            img = 'ocr/large-images/letters/%s-%02d-%02d.png' % (photo_id, j, i)
            if not os.path.exists(img):
                sys.stderr.write('Missing %s\n' % img)
                continue
            dest_dir = 'ocr/large-images/by-letter/%s' % escape_letter(char)
            mkdir_p(dest_dir)
            shutil.copy2(img, dest_dir)
            
# ocr/large-images/700078bu.jpg,700078f,40.8,67.6,0.8909002235013688,622,3448.959228515625,2453,3217.71240234375
