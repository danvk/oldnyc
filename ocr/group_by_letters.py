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


for row in csv.DictReader(open('ocr/transcribe/output.csv')):
    photo_id = row['photo_id']
    num_cols = row['num_cols']
    num_rows = row['num_rows']
    transcription = row['transcription']

    for j, line in enumerate(transcription.split('\n')):
        for i, char in enumerate(line):
            if char == '\r' or char == ' ': continue
            img = 'ocr/images/letters/%s-%02d-%02d.png' % (photo_id, j, i)
            if not os.path.exists(img):
                sys.stderr.write('Missing %s\n' % img)
                continue
            dest_dir = 'ocr/images/by-letter/%s' % char
            mkdir_p(dest_dir)
            shutil.copy2(img, dest_dir)
