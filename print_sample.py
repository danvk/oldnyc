#!/usr/bin/python
import locatable
import record
import sample

print """
<html>
<head><title>Records</title></head>
<body>
<table>
<tr><th>ID</th><th>Date</th><th>Title</th><th>Location</th></tr>
"""

N = 1000
sample = sample.LoadSample("records/*", N)
for r in sample:
  if not locatable.IsLocatable(r):
    pass
  print "<tr><td><a href='%s'>%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
    r.preferred_url, r.photo_id, r.date, r.title, r.location)


print "</table>"
print "</body></html>"
