#!/bin/bash
# Runs ocropy on an image, producing text output.
# Usage:
# ./run-ocropy.sh model.pyrnn.gz image.jpg output.txt
#
# TODO: run a bunch of images at once; model loading is expensive.

if [[ $# -ne 3 ]]; then
    >&2 echo "Wrong # of arguments"
    exit 1
fi

model=$1
input=$2
output=$3
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

set -o errexit

test -f $model
test -f $input

if [ -d /tmp/book ]; then
  rm -rf /tmp/book
fi

ocropus-nlbin $input -o /tmp/book
ocropus-gpageseg \
  --maxcolseps 0 \
  --json_output /tmp/book/lines.json \
  /tmp/book/????.bin.png

# TODO: might want to pass -n here to pick up "(1)"-type short lines.
ocropus-rpred -Q 4 -m $model /tmp/book/????/??????.bin.png

set +o errexit

$DIR/extract_ocropy_text.py /tmp/book/lines.json > $output
