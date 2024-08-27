#!/usr/bin/env python

import json
from ocr.url_fetcher import Fetcher


def get_nypl_fetcher(throttle_secs=1):
    token = open('.nypl-token.txt').read()
    f = Fetcher(
        headers={'Authorization': f'Token token="{token}"'},
        throttle_secs=throttle_secs
    )
    return f


if __name__ == '__main__':
    f = get_nypl_fetcher()
    roots_bytes = f.fetch_url('https://api.repo.nypl.org/api/v2/items/roots')
    roots = json.loads(roots_bytes)
    uuids = roots['nyplAPI']['response']['uuids']['uuid']
    with open('crawl/roots.json', 'w') as out:
        json.dump({'uuids': uuids}, out)
