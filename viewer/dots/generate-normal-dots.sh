#!/bin/bash

color='#111111'
stroke_color='#111111'
#text_color='#ffffff'
text_color='#111111'
font=Helvetica-Bold

convert -size 9x9 xc:none -fill 'rgb(160,160,160)' -draw 'circle 4,4 7,7' 1.png

for x in $(seq 2 100); do
  shade=$( echo "floor(160 - 160 * $x/100)" | bc)
  rgb="rgb($shade,$shade,$shade)"
  convert -size 13x13 xc:none -fill $rgb -draw 'circle 6,6 10,10' $x.png
done

montage $(ls ?.png ??.png ???.png | sort -n | xargs) -background transparent -gravity NorthWest -geometry '39x39>+0+0' -tile 10x ../static/images/sprite-2014-08-29.png

rm ?.png ??.png ???.png
