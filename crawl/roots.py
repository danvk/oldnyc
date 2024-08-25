#!/usr/bin/env python

import json
from ocr.url_fetcher import Fetcher

if __name__ == '__main__':
    token = open('.nypl-token.txt').read()
    f = Fetcher(headers={'Authorization': f'Token token="{token}"'})
    roots_bytes = f.fetch_url('https://api.repo.nypl.org/api/v2/items/roots')
    roots = json.loads(roots_bytes)
    uuids = roots['nyplAPI']['response']['uuids']['uuid']
    with open('crawl/roots.json', 'w') as out:
        json.dump({'uuids': uuids}, out)
