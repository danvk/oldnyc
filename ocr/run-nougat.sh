#!/usr/bin/env bash
set -o errexit

# NOUGAT_MODEL=0.1.0-base

# # Step 1: rotate to match NYPL images
# rm -rf /tmp/rotated
# mkdir /tmp/rotated
# for file in "$1"/*.jpg; do
#     ./ocr/rotate_ocrback.py $file /Users/danvk/Documents/oldnyc/images/$(basename $file) /tmp/rotated
# done

# Step 2: crop
rm -rf /tmp/crops
mkdir /tmp/crops
./ocr/tess/crop_morphology.py --beta 2 --output_pattern '/tmp/crops/%s.png' '/tmp/rotated/*.jpg' '/tmp/rotated/*.png'

# Step 3: increase contrast, cap width, convert to JPEG
rm -rf /tmp/contrast-1500
mkdir /tmp/contrast-1500
for file in /tmp/crops/*.png; do
    base=$(basename $file)
    jpg=${base/.png/.jpg}
    magick $file -contrast-stretch 10x10 -resize '1500>' -quality 90 /tmp/contrast-1500/$jpg
done
#
# # Step 4: Tesseract
# rm -rf /private/tmp/tesseract
# mkdir /private/tmp/tesseract
# for file in /private/tmp/contrast-1500/*.jpg; do
#      base=$(basename $file)
#      noext=${base/.jpg/}
#      echo $noext
#      tesseract $file /private/tmp/tesseract/$noext -l eng
# done

# Step 4: OCR
# rm -rf /tmp/nougat-out
# mkdir /tmp/nougat-out
# for file in /tmp/crops/*.pdf; do
#     base=$(basename $file)
#     mmd=/tmp/nougat-out/${base/.pdf/.mmd}
#     touch $mmd
#     set +o errexit
#     timeout 60 nougat --recompute --no-skipping --model $NOUGAT_MODEL $file -o /tmp/nougat-out
#     EXIT_STATUS=$?
#     set -o errexit
#     if [ $EXIT_STATUS -eq 124 ]; then
#         echo Nougat timed out on $file
#         echo '[Nougat Timeout]' > $mmd
#     elif [ $EXIT_STATUS -ne 0 ]; then
#         echo 'Nougat failure'
#         exit $EXIT_STATUS
#     fi
# done
