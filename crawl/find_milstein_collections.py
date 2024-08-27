#!/usr/bin/env python

import sys
import json
from crawl.roots import get_nypl_fetcher

if __name__ == '__main__':
    f = get_nypl_fetcher()
    uuids = json.load(open('crawl/roots.json'))['uuids']
    print(f'Founds {len(uuids)} roots')
    milsteins = []
    for i, uuid in enumerate(uuids):
        print(f'{i}: {uuid}')
        raw = f.fetch_url(f'https://api.repo.nypl.org/api/v2/mods/{uuid}')
        data = json.loads(raw)
        try:
            locs = data['nyplAPI']['response']['mods']['location']
            in_milstein = '"$": "Milstein Division"' in json.dumps(locs)
            if in_milstein:
                print(f'Hit on {uuid}')
                milsteins.append(uuid)
        except KeyError:
            sys.stderr.write(f'Failed to get location for {uuid}...\n')

        with open('crawl/milsteins.json', 'w') as out:
            json.dump({'collections': milsteins}, out)
