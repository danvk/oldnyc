#!/usr/bin/env bash
set -o errexit
set -x

# Step 1: rotate to match NYPL images
rm -rf /tmp/rotated
mkdir /tmp/rotated
for file in "$1"/*.jpg; do
    ./ocr/rotate_ocrback.py $file /Users/danvk/Documents/oldnyc/golden-100/$(basename $file) /tmp/rotated
done

# Step 2: crop
rm -rf /tmp/crops
mkdir /tmp/crops
./ocr/tess/crop_morphology.py --output_pattern '/tmp/crops/%s.png' '/tmp/rotated/*.jpg' '/tmp/rotated/*.png'

# Step 3: convert to PDF
for file in /tmp/crops/*.png; do
    convert $file ${file/.png/.pdf}
done

# Step 4: OCR
rm -rf /tmp/nougat-out
mkdir /tmp/nougat-out
for file in /tmp/crops/*.pdf; do
    set +o errexit
    timeout 60 nougat $file -o /tmp/nougat-out
    set -o errexit
    EXIT_STATUS=$?
    if [ $EXIT_STATUS -eq 124 ]; then
        echo Nougat timed out on $file
        echo '[Nougat Timeout]' > /tmp/nougat-out/${$(basename $file)/.pdf/.mmd}
    elif [ $EXIT_STATUS -ne 0 ]; then
        echo 'Nougat failure'
        exit $EXIT_STATUS
    fi
done
