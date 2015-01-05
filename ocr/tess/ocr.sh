#!/bin/bash
# Usage: ./ocr.sh path/to/images/*.jpg

# This:
# 1. Intelligently crops the image
# 2. Runs a first-pass OCR to find over-wide letters
# 3. Splits the over-wide letters
# 4. Runs final-pass OCR
set -o errexit
set -x

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

for img in "$@"; do
  #  Intelligently crop the image
  $DIR/crop_morphology.py $img
  cropped=${img/.jpg/.crop.png}
  test -f $cropped
  mv $cropped /tmp/crop.png

  # 2. Run first-pass OCR to find over-wide letters
  tesseract /tmp/crop.png /tmp/crop batch.nochop makebox
  test -f /tmp/crop.box

  # 3. Split over-wide letters
  $DIR/mark_wide_boxes.py /tmp/crop.box /tmp/crop.png
  test -f /tmp/crop.separated.png

  # 4. Run final-pass OCR
  tesseract /tmp/crop.separated.png $img
  test -f $img.txt

  # Generate raw tesseract output for comparison
  tesseract $img $img.raw
done
