#!/usr/bin/python
import re
import record

# build a photo_id -> Record dict
rs = record.AllRecords()
id_to_record = {}
for r in rs:
  id_to_record[r.photo_id()] = r

# load the list of geocodes
lines = file('/tmp/pair-geocodes.txt').read().split('\n')
codes = []
for line in lines:
  if not line: continue

  # e.g. AAB-2914<tab>37.723611,-122.400803
  photo_id = line.split("\t")[0]
  lat_lon = line.split("\t")[1]
  lat, lon = [float(x) for x in lat_lon.split(",")]
  codes.append((photo_id, lat, lon))


print """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
"""

for photo_id, lat, lon in codes:
  r = id_to_record[photo_id]
  date = record.CleanDate(r.date())
  title = record.CleanTitle(r.title())
  folder = r.location() or ''
  if folder: folder = record.CleanFolder(folder)
  note = r.note() or ''

  print """
  <Placemark>
    <name>%s</name>
    <description>
      <![CDATA[
        <a href="%s"><img width="150" align="right" src="%s" /></a>
        %s<br/>
        %s<br/>
        %s
      ]]>
    </description>
    <Point>
      <coordinates>%f,%f</coordinates>
    </Point>
  </Placemark>""" % (date, r.preferred_url, r.photo_url,
                     title, note, folder, lon, lat)

print """
  </Document>
</kml>
"""
