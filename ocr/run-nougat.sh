#!/usr/bin/env bash
set -o errexit

# for id in $(cat "$1"); do
#     echo $id
# done

# Step 1: crop
rm -rf /tmp/crops
mkdir /tmp/crops
./ocr/tess/crop_morphology.py --output_pattern '/tmp/crops/%s.png' "$1"'/*.jpg'

# Step 2: convert to PDF
for file in /tmp/crops/*.png; do
    convert $file ${file/.png/.pdf}
done

# Step 3: OCR
rm -rf /tmp/nougat-out
mkdir /tmp/nougat-out
for file in /tmp/crops/*.pdf; do
    nougat $file -o /tmp/nougat-out
done
