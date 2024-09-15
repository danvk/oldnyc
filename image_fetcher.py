#!/usr/bin/python
#
# Fetch full images from the library for a random subset of records.

from optparse import OptionParser
import fetcher
import random
import record


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-n", "--num", dest="num",
                    default=100,
                    help="How many images to fetch.")
  parser.add_option("", "--seed", dest="seed", default=12345,
                    help="Random number seed.")
  parser.add_option("-c", "--output_dir", dest="cache_dir", default="images",
                    help="Images destination dir")
  parser.add_option("-s", "--secs", dest="secs", default=5,
                    help="Number of seconds to wait between fetches.")

  (options, args) = parser.parse_args()

  rs = record.AllRecords()
  rand = random.Random(options.seed)
  rand.shuffle(rs)
  f = fetcher.Fetcher(options.cache_dir, int(options.secs))
  for i, r in enumerate(rs[0:int(options.num)]):
    print("%03d Fetching %s" % (i, r.photo_url))
    f.Fetch(r.photo_url)
