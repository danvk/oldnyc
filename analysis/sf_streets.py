#!/usr/bin/python
#
# Go through the list of records and find geocodable street information.
#
# Input:
#    records.pickle
#    street-list.txt (a manually-generated list of street names)
#
# Output:
#    /tmp/sf-crossstreets.pickle
#       Format is [ [photo_id, street folder, [ cross streets ] ], ... ]

import sys
sys.path += (sys.path[0] + '/..')

import re
import record
import cPickle

output_mode = 'pickle'

# TODO(danvk): all the functions here should go into an object.

def get_street_cat(cat):
  st = cat.split('-')[1]
  if '1920' in st or 'Unidentified' in st or 'Bernal Cut' in st: return None
  return st


def clean_street_cat(st):
  st = st.replace('21th', '21st')
  st = st.replace('farralon', 'farallones')
  st = st.replace('keanry', 'kearny')
  st = st.replace('kearney', 'kearny')
  st = st.replace('deharo', 'de haro')
  st = st.replace('water main', 'watermain')  # hack
  st = st.replace('noe valley', 'noevalley')  # hack
  st = st.replace('in front', 'infront')  # hack
  st = st.replace('store front', 'storefront')  # hack
  st = re.sub(r'farralon\b', 'farallones', st)
  st = re.sub(r'douglas\b', 'douglass', st)
  st = re.sub(r'boulevard|blvd|avenue|\bave\b|street|\broad\b|\brd\b', '', st)
  st = re.sub(r'\(.*', '', st)
  st = re.sub(r'^ *', '', st)
  st = re.sub(r' *$', '', st)
  st = re.sub(r'\.$', '', st)
  st = re.sub(r' *$', '', st)
  return st


def ordinal_shrinker(st):
  st = st.replace('twentieth', '20th')
  st = st.replace('twenty-first', '21st')
  st = st.replace('twenty-second', '22nd')
  st = st.replace('twenty-third', '23rd')
  st = st.replace('twenty-fourth', '24th')
  st = st.replace('twenty-fifth', '25th')
  st = st.replace('twenty-sixth', '26th')
  st = st.replace('twenty-seventh', '27th')
  st = st.replace('twenty-eighth', '28th')
  st = st.replace('twenty-ninth', '29th')
  st = st.replace('thirtieth', '30th')
  st = st.replace('thirty-first', '31st')
  st = st.replace('thirty-second', '32nd')
  st = st.replace('thirty-third', '33rd')
  st = st.replace('thirty-fourth', '34th')
  st = st.replace('thirty-fifth', '35th')
  st = st.replace('thirty-sixth', '36th')
  st = st.replace('thirty-seventh', '37th')
  st = st.replace('thirty-eighth', '38th')
  st = st.replace('thirty-ninth', '39th')
  st = st.replace('fortieth', '40th')
  st = st.replace('forty-first', '41st')
  st = st.replace('forty-second', '42nd')
  st = st.replace('forty-third', '43rd')
  st = st.replace('forty-fourth', '44th')
  st = st.replace('forty-fifth', '45th')
  st = st.replace('forty-sixth', '46th')
  st = st.replace('forty-seventh', '47th')
  st = st.replace('forty-eighth', '48th')
  st = st.replace('forty-ninth', '49th')
  st = st.replace('first', '1st')
  st = st.replace('second', '2nd')
  st = st.replace('third', '3rd')
  st = st.replace('fourth', '4th')
  st = st.replace('fifth', '5th')
  st = st.replace('sixth', '6th')
  st = st.replace('seventh', '7th')
  st = st.replace('eighth', '8th')
  st = st.replace('ninth', '9th')
  st = st.replace('tenth', '10th')
  st = st.replace('eleventh', '11th')
  st = st.replace('twelfth', '12th')
  st = st.replace('thirteenth', '13th')
  st = st.replace('fourteenth', '14th')
  st = st.replace('fifteenth', '15th')
  st = st.replace('sixteenth', '16th')
  st = st.replace('seventeenth', '17th')
  st = st.replace('eighteenth', '18th')
  st = st.replace('nineteenth', '19th')
  return st


def kill_substrings(arr):
  """Kills any element which is a substring of another element."""
  for i in reversed(range(0, len(arr))):
    kill = False
    for j in range(0, len(arr)):
      if i != j and arr[i] in arr[j]:
        kill = True
    if kill:
      del arr[i]


tiny_streets = [
  'maiden lane', 
  'juri', 
  'myra way', 
  'naglee', 
  'niantic', 
  'ogden', 
  'onondaga', 
  'peralta', 
  'phelan', 
  'quane street', 
  'ripley', 
  'ritch street', 
  'st. francis circle', 
  'steuart', 
  'tehama street', 
  'villa terrace', 
  'balance street', 
  'barcelona',
  'hotaling place',
  'hattie',
  'jordan'
]

def extract_matches(txt, st, street_list, res):
  """txt is text that may contain street information. Exclude street st from
  consideration. Returns an array of street matches."""
  street_txt = clean_street_cat(ordinal_shrinker(txt))
  matches = []
  for idx, cross_street in enumerate(street_list):
    if cross_street != st and re.search(res[idx], street_txt):
      matches.append(cross_street)

  # special case: make sure we don't match "second" _and_ "twenty-second".
  kill_substrings(matches)

  if not st and len(matches) == 1:
    st = matches[0]

  # e.g. "2500 block of lombard"
  if '00 block' in street_txt:
    m = re.search(r'(\d+00) block', street_txt)
    matches.append('block: ' + m.group(1))

  # e.g.  "652  miramar avenue"
  if st:
    rst = st
    if rst == '3rd': rst = 'third'
    if rst == '4th': rst = 'fourth'
    if rst == '6th': rst = 'sixth'
    m = re.search(r'([-0-9 ]+) *' + rst + r'( (street|avenue|ave|road|boulevard|blvd|place|way))?', txt)
    if m and re.search(r'\d', m.group(1)):
      matches.append('address:' + m.group(0))

  # Fallback: some streets are short enough that they're geocodable.
  if not matches:
    for tiny_street in tiny_streets:
      if tiny_street in street_txt:
        matches.append("tiny:" + tiny_street)

  return matches


if __name__ == '__main__':
  street_list = file("street-list.txt").read().split("\n")
  street_list = [s.lower() for s in street_list if s]

  res = []
  for cross_street in street_list:
    res.append(re.compile(r'\b' + cross_street + r'\b'))

  outputs = []
  rs = record.AllRecords()
  for r in rs:
    loc = r.location()
    loc = loc.replace('Folder: S.F. Earthquakes-1906-Streets',
                      'Folder: S.F. Streets')
    loc = loc.replace('Sheet: S.F. Streets', 'Folder: S.F. Streets')
    if not loc.startswith("Folder: S.F. Streets-"): continue
    st = get_street_cat(loc)
    if not st: continue
    st = clean_street_cat(st.lower())

    title = record.CleanTitle(r.title()).lower()
    matches = extract_matches(title, st, street_list, res)

    if output_mode == 'text':
      print "%s\t%s\t%s\t%s" % (r.photo_id(), st, matches, title)
    elif output_mode == 'pickle':
      outputs.append([r.photo_id(), st, matches])

  print len(outputs)
  if outputs:
    cPickle.dump(outputs, file('/tmp/sf-crossstreets.pickle', 'w'))
