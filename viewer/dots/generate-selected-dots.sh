#!/bin/bash

#color='#111111'
#color='#26264A'
color='#0000A0'
stroke_color=$color
text_color=$color  # '#ffffff'
font=Helvetica-Bold

# Third & fourth circle parameters are a point on the circle's circumference.
convert -size 15x15 xc:none -fill $color -draw 'circle 7,7 13,7' 1.png

for x in $(seq 2 100); do
  convert -size 21x21 xc:none -fill $color -stroke $stroke_color -draw 'circle 10,10 19,10' $x.png
done

montage $(ls ?.png ??.png ???.png | sort -n | xargs) -background transparent -gravity NorthWest -geometry '39x39>+0+0' -tile 10x ../static/images/selected-2014-08-29.png

rm ?.png ??.png ???.png
