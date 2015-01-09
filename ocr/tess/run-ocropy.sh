#!/bin/bash
# Runs ocropy on an image, producing text output.
# Usage:
# ./run-ocropy.sh model.pyrnn.gz image1.jpg image2.jpg ...

if [[ $# -lt 2 ]]; then
    >&2 echo "Wrong # of arguments"
    exit 1
fi

model=$1
test -f $model
shift
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

set -o errexit

bin_patterns=''
patterns=''
for input in "$@"; do
  book=/tmp/book-${input/.jpg/}
  if [ -d $book ]; then
    rm -rf $book
  fi
  echo $input
  echo $book
  ocropus-nlbin -n $input -o $book

  bin_patterns="$bin_patterns $book/????.bin.png"
  patterns="$patterns $book/????/??????.bin.png"
done

ocropus-gpageseg \
  -n \
  --maxcolseps 0 \
  $bin_patterns

ocropus-rpred -n -Q 4 -m $model $patterns

set +o errexit

for input in "$@"; do
  book=/tmp/book-${input/.jpg/}
  ocropus-hocr -o $book/book.html $book/????.bin.png
  $DIR/extract_ocropy_text.py $book/book.html > $input.txt
done
