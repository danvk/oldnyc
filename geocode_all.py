#!/usr/bin/python
import random
import re
import record
import geocoder
from optparse import OptionParser

def CodeAll(fetch):
  rs = record.AllRecords()
  addys = [(r.locatable_str(), r.title()) for r in rs if r.locatable_str()]

  if not fetch:
    for idx, a in enumerate(addys):
      (loc, title) = a
      print "[%s] from %s" % (loc, title)
    print "Extracted %d addresses" % len(addys)
    return

  g = geocoder.Geocoder("ABQIAAAAafDALeUVyxhUndZQcT0BRRQjgiEk1Ut90lZbiCSD8tXKcVgrkBQLYOFQ3xwutc5R9SNzfGaKxMnf7g", 5)

  for idx, a in enumerate(addys):
    print "%4d " % idx,
    addr = a[0]
    x = g.Locate(addr)
    if x.status != 200:
      print "%s -> status %d" % (addr, x.status)
    else:
      try:
        print "%s -> %d @ %d (%s %f,%f)" % (addr, x.status, x.accuracy, x.city, x.lat, x.lon)
      except:
        print "%s is weird" % addr


def PrintRandom(n):
  rs = record.AllRecords()
  addys = [r.title() for r in rs if not r.locatable_str()]
  random.shuffle(addys)
  for addy in addys[0:n]:
    addy = re.sub('^\[', '', addy)
    addy = re.sub(' \[graphic\]\.$', '', addy)
    addy = re.sub('\]$', '', addy)
    print addy


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-f", "--fetch", dest="fetch", default=False,
                    help="Should request actually be sent on the network?")
  parser.add_option("-r", "--random", dest="random", default=0,
                    help="Set to see a random subset of non-locatable titles")
  (options, args) = parser.parse_args()

  if options.random > 0:
    PrintRandom(int(options.random))
  else:
    CodeAll(options.fetch)
