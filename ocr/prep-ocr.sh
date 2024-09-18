#!/usr/bin/env bash
set -o errexit

SMALL_IMG_DIR=/Users/danvk/Documents/oldnyc/images
LARGE_IMG_DIR='/Volumes/teradan/Milstein Images/ocrbacks'

TESSERACT_DIR=/Users/danvk/Documents/oldnyc/tesseract
GPT_DIR=/Users/danvk/Documents/oldnyc/gpt

ids_file="$1"

# Step 1: rotate to match NYPL images
echo 'Rotating images'
rm -rf /tmp/rotated
mkdir /tmp/rotated
while read -r imageid; do
    echo "$imageid"
    large_file="$LARGE_IMG_DIR"/$imageid
    small_file="$SMALL_IMG_DIR"/$imageid.jpg
    ./ocr/rotate_ocrback.py "$large_file" "$small_file" /tmp/rotated
done < "$ids_file"

# Step 2: crop
echo 'Cropping to text'
rm -rf /tmp/crops
mkdir /tmp/crops
./ocr/tess/crop_morphology.py --beta 2 --output_pattern '/tmp/crops/%s.png' '/tmp/rotated/*.jpg' '/tmp/rotated/*.png'

# Step 3: increase contrast, cap width, convert to JPEG
# TODO: "1500" makes no sense any more
echo 'Resizing and increasing contrast'
rm -rf /tmp/contrast-1500
mkdir /tmp/contrast-1500
for file in /tmp/crops/*.png; do
    base=$(basename $file)
    jpg=${base/.png/.jpg}
    magick $file -contrast-stretch 10x10 -resize '2048x768>' -quality 90 /tmp/contrast-1500/$jpg
done

# Step 4: Tesseract
echo 'Running Tesseract'
rm -rf /private/tmp/tesseract
mkdir /private/tmp/tesseract
for file in /private/tmp/crops/*.png; do
     base=$(basename $file)
     noext=${base/.jpg/}
     noext=${base/.png/}
     # echo $noext
     tesseract $file $TESSERACT_DIR/$noext -l eng
done

# Step 5: Produce a GPT batch
echo 'Generating GPT batch file'
gpt_out=$GPT_DIR/$(basename $ids_file).jsonl
./ocr/generate_gpt_batch.py \
    --model gpt-4o-mini \
    --image_directory /tmp/contrast-1500 \
    "$ids_file" \
    > "$gpt_out"

echo 'All done!'

# Step 4: OCR
# rm -rf /tmp/nougat-out
# mkdir /tmp/nougat-out
# for file in /tmp/pdfs/*.pdf; do
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