from nose.tools import *

from split_wide_boxes import *
from box import BoxLine

def test_nosplit():
  box = BoxLine.parse_line('C 79 405 90 420 0')
  boxes = split_box(box)
  eq_(['C 79 405 90 420 0'], [str(x) for x in boxes])

def test_split2():
  box = BoxLine.parse_line('C 66 405 90 420 0')
  boxes = split_box(box)
  eq_(['C 66 405 78 420 0',
       'C 78 405 90 420 0'],
          [str(x) for x in boxes])

def test_split22():
  box = BoxLine.parse_line('C 66 405 88 420 0')
  boxes = split_box(box)
  eq_(['C 66 405 77 420 0',
       'C 77 405 88 420 0'],
          [str(x) for x in boxes])
