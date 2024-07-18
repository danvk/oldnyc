#!/usr/bin/env python
'''Kill titles which are redundant with the location, e.g.

Manhattan: 8th Avenue - 24th Street (West)
'''

import fileinput
import re

boros = r'(?:New York|Manhattan|Brooklyn|Bronx|Queens|Staten Island|Richmond)'
streets = r'(?:St\.|Street|Place|Pl\.|Road|Rd\.|Avenue|Ave\.|Av\.|Boulevard|Blvd\.?|Broadway|Parkway|Pkwy\.?|Pky\.?|Street \(West\)|Street \(East\)|Drive|Lane)'

patterns = [
    boros + r': ([^-,]*?) - ([^-,]*?)$'
]

def is_pure_location(title):
    for pattern in patterns:
        m = re.match(pattern, title)
        if m:
            street1, street2 = m.groups()
            if re.search(streets, street1) and re.search(streets, street2):
                return True
    return False


if __name__ == '__main__':
    for line in fileinput.input():
        line = line.strip()
        print('%s %s' % ('x' if is_pure_location(line) else ' ', line))
