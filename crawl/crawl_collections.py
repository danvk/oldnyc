#!/usr/bin/env python

import json
import requests
import time
from crawl.roots import get_nypl_fetcher


collection_url = 'https://api.repo.nypl.org/api/v2/collections/%s/items?per_page=100'
items_url = 'https://api.repo.nypl.org/api/v2/collections/%s/items?per_page=%d&page=%d'
captures_url = 'https://api.repo.nypl.org/api/v2/items/collection/%s?per_page=%d&page=%d'

ITEMS_PER_PAGE = 500


def as_list(dict_or_list):
    return [dict_or_list] if isinstance(dict_or_list, dict) else dict_or_list


if __name__ == '__main__':
    f = get_nypl_fetcher(throttle_secs=3)
    uuids = json.load(open('crawl/milsteins.json'))['collections']
    print(f'Will crawl from {len(uuids)} collections.')

    queue = [
        # type, uuid
        ('collection', uuid) for uuid in uuids
    ]
    all_items = []
    all_urls = []
    all_captures = []

    while queue:
        item = queue[0]
        print(f'{item} queue length: {len(queue)}')
        queue = queue[1:]
        typ, uuid = item[:2]
        if typ == 'collection':
            url = collection_url % uuid
            raw = f.fetch_url(url)
            all_urls.append(url)
            data = json.loads(raw)
            response = data['nyplAPI']['response']
            num_sub = int(response['numSubCollections'])
            num_items = int(response['numItems'])
            print(f'{uuid}: {num_sub} / {num_items}')
            if 'item' in response:
                item_list = as_list(response['item'])
                if len(item_list) < 100:
                    all_items += item_list
                    print(f'All items: {len(all_items)}')
                else:
                    # it's one above the leaves. Re-crawl it as items.
                    for i, start in enumerate(range(0, num_items, ITEMS_PER_PAGE)):
                        queue.append(('items', uuid, ITEMS_PER_PAGE, i))
                        queue.append(('captures', uuid, ITEMS_PER_PAGE, i))
            if 'collection' in response:
                collections_list = as_list(response['collection'])
                if num_sub > len(collections_list):
                    print(f'{uuid} may have a truncated collections list')
                for collection in collections_list:
                    uuid = collection['uuid']
                    num_sub = int(collection['numSubCollections'])
                    num_items = int(collection['numItems'])
                    if num_sub == 0:
                        for i, start in enumerate(range(0, num_items, ITEMS_PER_PAGE)):
                            queue.append(('items', uuid, ITEMS_PER_PAGE, i))
                            queue.append(('captures', uuid, ITEMS_PER_PAGE, i))
                    else:
                        queue.append(('collection', uuid))
        elif typ == 'items':
            url = items_url % item[1:]
            all_urls.append(url)
            try:
                raw = f.fetch_url(url)
            except requests.exceptions.HTTPError as e:
                if '502 Server Error' in str(e):
                    print(f'Got 502 on {url}, waiting 5s and trying again')
                    time.sleep(5)
                    queue.append(item)
                    continue
                else:
                    raise e
            data = json.loads(raw)
            response = data['nyplAPI']['response']
            if 'item' not in response:
                # must have been a collection
                # print(data)
                continue
            all_items += as_list(response['item'])
            print(f'All items: {len(all_items)}')
        elif typ == 'captures':
            url = captures_url % item[1:]
            print(url)
            all_urls.append(url)
            try:
                raw = f.fetch_url(url)
            except requests.exceptions.HTTPError as e:
                if '502 Server Error' in str(e):
                    print(f'Got 502 on {url}, waiting 5s and trying again')
                    time.sleep(5)
                    queue.append(item)
                    continue
                else:
                    raise e
            data = json.loads(raw)
            response = data['nyplAPI']['response']
            try:
                all_captures += as_list(response['capture'])
                print(f'All captures: {len(all_captures)}')
                with open('crawl/milstein-captures.json', 'w') as out:
                    json.dump({'captures': all_captures}, out, indent=None)
            except KeyError:
                print('Failed to get captures')

    with open('crawl/milstein-items.json', 'w') as out:
        json.dump({'items': all_items}, out, indent=None)
    with open('crawl/milstein-captures.json', 'w') as out:
        json.dump({'captures': all_captures}, out, indent=None)
    with open('crawl/all-urls.txt', 'w') as out:
        print(f'num urls: {len(all_urls)}')
        out.write('\n'.join(all_urls))
        out.write('\n')
