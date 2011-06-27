#!/usr/bin/python
#
# Usage:
#   import record
#   rs = record.AllRecords()
#   print rs[0].photo_url
#   ...

import cPickle
import re
import time
import sys
from datetime import date
from datetime import timedelta

def ExtractRegex(pat, str):
  """Return the first captured string of the regex or None if there was no match."""
  m = re.search(pat, str, re.DOTALL)
  if not m: return None
  try:
    return m.group(1)
  except IndexError:
    return None

def strip_tags(value):
  "Return the given HTML with all tags stripped."
  # TODO(danvk): replace this with something correct.
  return re.sub(r'<[^>]*?>', '', value)

def parse_month(mon):
  """Takes "Jan" -> 1"""
  return int(time.strptime(mon[0:3], "%b")[1])

Tags = {}
class Record:
  def __init__(self):
    self._date_range = None

  @staticmethod
  def FromString(str):
    if re.search(r'No Such Record', str):
      return None

    # Want to get:
    # - Thumbnail URL
    # - Full image URL
    # - All tabular data (e.g. Subject, Description, Date, etc.)
    # - The library's preferred URL
    r = Record()
    r.thumbnail_url = ExtractRegex(r'<img src="([^"]*/thumbnails/[^"]*)"', str)
    r.photo_url = ExtractRegex(r'href="([^"]*/sfphotos/[^"]*)"', str)
    r.preferred_url = ExtractRegex(r'name="LinkURL"[^>]*value="([^"]+)"', str)

    r.tabular = {}
    m = re.search(r'<!-- BEGIN INNER BIB TABLE -->(.*?)<!-- END INNER BIB TABLE -->', str, re.DOTALL)
    if m:
      fields_html = m.group(1).split('next row for fieldtag=')
      for field_html in fields_html[1:]:
        field_tag = field_html[0]
        if field_tag not in r.tabular:
          r.tabular[field_tag] = []
        val_html = ExtractRegex(r'<td class="bibInfoData">(.*?)</td>', field_html)
        assert val_html
        r.tabular[field_tag].append(val_html.strip())

        # class="bibInfoLabel">Subject<
        tag_name = ExtractRegex(r'class="bibInfoLabel">([^<]+)', field_html)
        if tag_name:
          if field_tag not in Tags: Tags[field_tag] = {}
          Tags[field_tag][tag_name] = 1 + Tags[field_tag].setdefault(tag_name, 0)

    # Create nice accessors for some common properties.
    # easy_tags = {
    #   'l': 'location',
    #   'i': 'photo_id',
    #   'p': 'date',
    #   'r': 'description',
    #   't': 'title',
    #   'n': 'notes'
    # }
    # for k, long_name in easy_tags.iteritems():
    #   if k in r.tabular and len(r.tabular[k]) == 1:
    #     r.__dict__[long_name] = strip_tags(r.tabular[k][0])
    #   else:
    #     r.__dict__[long_name] = None

    return r

  def _single_table(self, tag):
    if tag not in self.tabular: return ''
    vals = self.tabular[tag]
    if len(vals) == 1: return strip_tags(vals[0])
    return ''

  def photo_id(self): return self._single_table('i')
  def location(self): return self._single_table('l')
  def date(self): return self._single_table('p')
  def description(self): return self._single_table('r')
  def title(self): return self._single_table('t')
  def note(self): return self._single_table('n')

  @staticmethod
  def TagIds():
    return Tags

  @staticmethod
  def MostCommonNameForTag(tag):
    assert tag in Tags
    most_freq = None
    freq = -1
    for (name, v) in tags[k].iteritems():
      if v > freq:
        most_freq = name
        freq = v
    return most_freq

  @staticmethod
  def ExtractDateRange(raw_txt):
    """Return a (first, last) tuple of datetime.date's from a string."""
    # TODO(danvk): pre-compile all these re's

    txt = re.sub(r'[\[\].]', '', raw_txt).strip()  # strip '[', ']' and '.'
    # Undateable, e.g. "[n.d.]"
    if txt == 'nd':
      return (None, None)

    # Just a year, e.g. "1928."
    year = ExtractRegex(r'^(\d{4})$', txt)
    if year:
      start = date(int(year), 1, 1)
      end = date(int(year), 12, 31)
      return (start, end)

    # A "circa" year, e.g. "[ca. 1915]"
    ca_year = ExtractRegex(r'^ca? ?(\d{4})$', txt)
    if ca_year:
      y = int(ca_year)
      start = date(y - 1, 1, 1)
      end = date(y + 1, 12, 31)
      return (start, end)

    # An uncertain year, e.g. "[1856?]"
    ca_year = ExtractRegex(r'^(\d{4})\?$', txt)
    if ca_year:
      y = int(ca_year)
      start = date(y - 1, 1, 1)
      end = date(y + 1, 12, 31)
      return (start, end)

    # An exact date with a 3-letter month abbrev., e.g. "1950 Aug. 25."
    m = re.match(r'^(\d{4}) ([A-Z][a-z]{2,3}) ?(\d{1,2})$', txt)
    if m:
      year, mon, day = m.groups()
      year, mon, day = int(year), parse_month(mon), int(day)

      # hacks to correct non-existent dates
      # I should notify the library of these.
      if mon == 4 and day == 31:
        mon, day = 5, 1
      if year == 1949 and mon == 2 and day == 29:
        mon, day = 3, 1
      if mon == 6 and day == 31:
        mon, day = 7, 1
      if mon == 2 and day == 31:
        mon, day = 3, 1
      if mon == 11 and day == 31:
        mon, day = 12, 1

      start = date(year, mon, day)
      return (start, start)

    # A month and year, e.g. "1971 Aug."
    m = re.match(r'^(\d{4}) ([A-Z][a-z]{2,3})$', txt)
    if m:
      year, mon = m.groups()
      year, mon = int(year), parse_month(mon)
      start = date(year, mon, 1)
      # This monstrosity determines the last day of the month
      end = (start + timedelta(days=+32)).replace(day=1) + timedelta(days=-1)
      return (start, end)

    # A decade, e.g. "[194-]"
    dec = ExtractRegex(r'^([12]\d\d)-$', txt)
    if dec:
      year = int(dec + '0')
      start = date(year, 1, 1)
      end = date(year + 9, 12, 31)
      return (start, end)

    # A century, e.g. "[19--]"
    # TODO(danvk): maybe throw these out? '19--' isn't very informative.
    cen = ExtractRegex(r'^([12]\d)--$', txt)
    if cen:
      year = int(cen + '00')
      start = date(year, 1, 1)
      end = date(year + 99, 12, 31)
      if cen == '18':
        start = date(1850, 1, 1)  # Photography isn't that old.
      return (start, end)

    return None

  def date_range(self):
    if self._date_range:
      return self._date_range
    if not self.date:
      self._date_range = (None, None)
    else:
      p = Record.ExtractDateRange(self.date)
      if not p:
        self._date_range = (None, None)
      else:
        self._date_range = p
    return self._date_range

  def date_range_str(self):
    """Returns a string representation of the record's date range"""
    p = self.date_range()
    if not p: return ""
    (start, end) = p
    if not start or not end: return "no date"

    return "[%d-%02d-%02d, %d-%02d-%02d]" % (
        start.year, start.month, start.day,
        end.year, end.month, end.day)

  def locatable_str(self):
    """Returns a string that might represent a geocodable location"""
    addr = ExtractAddress(self.title())
    if addr: return addr

    return None


def ExtractAddress(str):
  """Find an address in the string and return it. Returns None if no address."""
  pat = r'''\b(?<![',.])(\d{2,})(?: [A-Z](?:[a-z.]|'[A-Za-z])+)+\b'''

  # Iterate over all matches. We don't want to miss a real address because
  # there's a bad address (like '1969 World's Fair') before it.
  for addr_match in re.finditer(pat, str):
    # If the resulting address number is between 1850 and 2000 then it might be a
    # year. We require extra evidence that it's actually an address in this case
    # (e.g. a 'street' or 'avenue' in the address).
    num, addr = int(addr_match.group(1)), addr_match.group(0)

    # This filters out some oddities like "206 B." from "206 B.C."
    if len(re.findall('[A-Za-z]', addr)) < 2:
      continue

    if 1850 < num < 2000:
      # Some of these are hard-coded based on the data.
      if re.search(r'(?i)(?:\bst.?\b)|(?:\bave\.?\b)|street|avenue|Broadway|Laidley|Pine|Geary|Sloat|Bush|Mission|Market|Broderick|Washington|Van Ness', addr):
        return addr
    else:
      return addr

  # Look for a street intersection.
  # TODO: match numeric streets like "16th"
  street_types = "(?:[sS]treets?|[aA]venue|[bB]lvd\.?|[sS]t\.?|[aA]ve\.?)"  # e.g. "Avenue" or "St"
  street_name = "(?:(?: [A-Z](?:[a-z.]|'[A-Za-z])+)+)"
  pat = r'''((?: [A-Z](?:[a-z.]|'[A-Za-z])+)+) (?:and|&|at)((?: [A-Z](?:[a-z.]|'[A-Za-z])+)+)( %s)''' % street_types
  for addr_match in re.finditer(pat, str):
    street1, street2 = addr_match.group(1), addr_match.group(2)
    #print "%s -> (%s, %s)" % (str, street1, street2)

def AllRecords(path="records.pickle"):
  """Reads all records from the pickled file and returns a list."""
  unpickler = cPickle.Unpickler(open(path, 'r'))

  count = 0
  rs = []
  try:
    while True:
      r = unpickler.load()
      rs.append(r)
      count += 1
  except EOFError:
    pass

  sys.stderr.write("Loaded %d records\n" % count)
  return rs


if __name__ == "__main__":
  str = file("records/1032033").read()
  r = Record.FromString(str)
  print "photo_url: %s" % r.photo_url
  print "thumb_url: %s" % r.thumbnail_url
  print "preferred: %s" % r.preferred_url
  print ""
  print "location: %s" % r.location
  print "date: %s" % r.date
  print "desc: %s" % r.description
  for k in sorted(r.tabular.keys()):
    print "%s %s: (%d) %s" % (k, Record.MostCommonNameForTag(k),
                              len(r.tabular[k]), r.tabular[k])

# Mostly-complete set of field tags (with frequency):
#  a:
#       422 Collection Name
#  b:
#      1561 Source
#        19 Alt Auth
#         1 Photographer
#  c:
#       472 Call #
#  d:
#     10006 Subject
#  e:
#     10000 Reproduction Rights
#  i:
#     10006 Photo Id#
#  l:
#      9546 Location
#  n:
#      4691 Notes
#        18 Summary
#  p:
#     10006 Date
#  r:
#     10006 Description
#  s:
#     10006 Series
#  t:
#     10006 Title
#  x:
#      1793 Copy Negative
#         2 Negative
