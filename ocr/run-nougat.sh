#!/usr/bin/env bash
set -o errexit

NOUGAT_MODEL=0.1.0-base

# # Step 1: rotate to match NYPL images
# rm -rf /tmp/rotated
# mkdir /tmp/rotated
# for file in "$1"/*.jpg; do
#     ./ocr/rotate_ocrback.py $file /Users/danvk/Documents/oldnyc/images/$(basename $file) /tmp/rotated
# done
#
# # Step 2: crop
# rm -rf /tmp/crops
# mkdir /tmp/crops
# ./ocr/tess/crop_morphology.py --output_pattern '/tmp/crops/%s.png' '/tmp/rotated/*.jpg' '/tmp/rotated/*.png'
#
# # Step 3: increase contrast and convert to PDF
# for file in /tmp/crops/*.png; do
#     convert -contrast-stretch 10x10 $file ${file/.png/.pdf}
# done

# Step 4: OCR
rm -rf /tmp/nougat-out
mkdir /tmp/nougat-out
for file in /tmp/crops/*.pdf; do
    base=$(basename $file)
    mmd=/tmp/nougat-out/${base/.pdf/.mmd}
    touch $mmd
    set +o errexit
    timeout 60 nougat --recompute --no-skipping --model $NOUGAT_MODEL $file -o /tmp/nougat-out
    EXIT_STATUS=$?
    set -o errexit
    if [ $EXIT_STATUS -eq 124 ]; then
        echo Nougat timed out on $file
        echo '[Nougat Timeout]' > $mmd
    elif [ $EXIT_STATUS -ne 0 ]; then
        echo 'Nougat failure'
        exit $EXIT_STATUS
    fi
done
