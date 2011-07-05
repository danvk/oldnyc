#!/usr/bin/python

import record
rs = record.AllRecords()

no_date = 0
failures = 0
success = 0

for r in rs:
  dr = r.date_range()
  if not dr:
    failures += 1
    print 'Failure: %s' % r.date()
    continue

  if not dr[0] and not dr[1]:
    no_date += 1
    continue

  success += 1

print 'no date: %d' % no_date
print 'failure: %d' % failures
print 'success: %d' % success

# initial: 1717 failures
# "between YYYY and YYYY" -> 1213
# Drop uncertainty -> 872
# lowercase between -> 757
# abbreviate months -> 740
# "1915 Oct. 2-3" -> 667
# generalized between -> 648
# "YYYY-YYYY" or "YYYY-YY" -> 571
# "YYYY or YYYY" -> 485
# drop "ca" -> 446
# "Aug. 1971" -> 439
# "-1906" -> 375
# "YYYY - YYYY" -> 373
