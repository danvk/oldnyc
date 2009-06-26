#!/usr/bin/python
import geocoder
import glob
import locatable
import re
import record

print """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
"""

g = geocoder.Geocoder("ABQIAAAAafDALeUVyxhUndZQcT0BRRQjgiEk1Ut90lZbiCSD8tXKcVgrkBQLYOFQ3xwutc5R9SNzfGaKxMnf7g", 5)
rs = record.AllRecords()
addys = [(r.locatable_str(), r) for r in rs if r.locatable_str()]
for loc_str, r in addys:
  loc = g.LocateFromCache(loc_str)
  if not loc: continue

  if loc.lat and loc.lon:
    print """
    <Placemark>
      <name>%s</name>
      <description>
        <![CDATA[
          <a href="%s"><img width="150" align="right" src="%s" /></a>
          %s
          %s
        ]]>
      </description>
      <Point>
        <coordinates>%f,%f</coordinates>
      </Point>
    </Placemark>""" % (r.date(), r.preferred_url, r.photo_url,
                       r.title(), r.description(), loc.lon, loc.lat)

print """
  </Document>
</kml>
"""
