#!/usr/bin/python
#
# The goal here is to check whether any single-record geocodes can be extended
# to full categories.
#
# Specifically excluded are:
# o SF Residences
# o SF Streets (and variants)
# o anything in cat-codes

import sys
sys.path += (sys.path[0] + '/..')

import record
import re
from collections import defaultdict

# read in previous generalization responses
# folder -> 'y' or 'n'
responses = {}
for line in file('generalizations.txt').read().split('\n'):
  if not line: continue
  m = re.match(r'(.*):(.*)', line)
  assert m, line
  assert m.group(1) not in responses, line
  responses[m.group(1)] = m.group(2)


rs = record.AllRecords()
id_to_record = {}
for r in rs:
  id_to_record[r.photo_id()] = r

# blacklist existing catcodes
catcodes = [line.split(" : ")[1] for line in file("cat-codes.txt").read().split("\n") if line]
def IsCatCode(r):
  global catcodes
  cat = record.CleanFolder(r.location())
  if not cat: return False
  for geocat in catcodes:
    if cat.startswith(geocat):
      return True
  return False

# load geocodes: (photo_id)<tab>(lat,lon)<tab>loc_type<tab>locatable_str
# photo_id -> [("lat,lon",locatable_str), ...]
id_to_code = {}
lines = file('/tmp/geocodes.txt').read().split('\n')
for line in lines:
  if not line: continue
  parts = line.split("\t")
  photo_id = parts[0]
  latlon = parts[1]
  loc_type = parts[2]
  if loc_type != 'free-streets': continue

  if len(parts) > 3:
    locatable_str = '\t'.join(parts[3:])
  else:
    locatable_str = ''

  if photo_id in id_to_code: continue
  id_to_code[photo_id] = (latlon, locatable_str)

# category -> list of records in category
coded_cats = defaultdict(list)
folder_to_record = defaultdict(list)

for r in rs:
  if not r.location(): continue
  folder = record.CleanFolder(r.location())
  folder_to_record[folder].append(r)

  if r.photo_id() not in id_to_code: continue
  if r.location().startswith("Folder: S.F. Streets-"): continue
  if r.location().startswith('Folder: S.F. Earthquakes-1906-Streets'): continue
  if r.location().startswith('Sheet: S.F. Streets'): continue
  if r.location().startswith('Folder: S.F. Residences'): continue
  if IsCatCode(r): continue

  # now this is a record which has the potential to be generalized.
  latlon, locatable_str = id_to_code[r.photo_id()]
  coded_cats[folder].append((r.photo_id(), latlon, locatable_str))


def add_generalization(response, coded_cats, records, generalizations):
  """
  response = manual response (either 'y', 'n', or a photo id)
  coded_cats = list of (photo_id, latlon, loc_str) tuples for a folder.
  records = list of all records for the folder.
  generalizations = list of (photo_id, latlon, comment) (I/O param)"""
  latlons = set()
  id_to_latlon = {}
  id_to_desc = {}
  for id, latlon, desc in coded_cats:
    latlons.add(latlon)
    id_to_latlon[id] = latlon
    id_to_desc[id] = desc

  ll = None
  desc = ''
  if len(latlons) == 1:
    ll = latlons.pop()
    desc = 'Generalized from %s ("%s")' % (coded_cats[0][0], coded_cats[0][2])
  elif '-' in response:
    assert response in id_to_latlon, response
    ll = id_to_latlon[response]
    src_desc = id_to_desc[response]
    desc = 'Generalized from %s ("%s")' % (response, src_desc)
  else:
    # TODO(danvk): handle this case
    pass

  if not ll: return

  for r in recs:
    if r.photo_id() in id_to_latlon: continue
    generalizations.append((r.photo_id(), ll, desc))


saved = 0
generalizations = []
for folder in coded_cats.keys():
  if len(folder_to_record[folder]) == len(coded_cats[folder]):
    continue

  recs = folder_to_record[folder]  # list of record objects
  ccs = coded_cats[folder]         # list of (photo_id, latlon, loc_str) tuples

  if folder in responses:
    resp = responses[folder]
    if resp in ['y', 'yes'] or '-' in resp:
      count = len(recs) - len(ccs)
      saved += count
      add_generalization(resp, ccs, recs, generalizations)

    continue

  print folder
  print '  Located:'
  located = set()
  for id, latlon, locatable_str in ccs:
    print '    %s (%s)' % (locatable_str, latlon)
    located.add(id)
  print '  Others: %d' % (len(recs) - len(ccs))
  dated_rs = [(r.date(), r) for r in recs]
  for date, r in sorted(dated_rs):
    c = ' '
    if r.photo_id() in located: c = '*'
    print '   %s%s %15s %s %s' % (c, r.photo_id(),
                                  record.CleanDate(r.date()),
                                  record.CleanTitle(r.title()),
                                  r.preferred_url)
  print ''

  response = raw_input('generalize? (y or n or photo_id): ')
  if response in ['y', 'n', 'yes', 'no'] or '-' in response:
    file('generalizations.txt', 'a').write('%s:%s\n' % (folder, response))
  else:
    print '(Skipping)'

  print ''
  print ''
  print ''

sys.stderr.write('Saveable records: %d\n' % saved)
sys.stderr.write('Saved: %d\n' % len(generalizations))

for id, ll, desc in generalizations:
  print '%s\t%s\t%s' % (id, ll, desc)
