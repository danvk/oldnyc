#!/usr/bin/env python

import json
from crawl.roots import get_nypl_fetcher


collection_url = 'https://api.repo.nypl.org/api/v2/collections/%s/items'
items_url = 'https://api.repo.nypl.org/api/v2/collections/%s/items?per_page=%d&page=%d'

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

    while queue:
        item = queue[0]
        print(f'{item} queue length: {len(queue)}')
        queue = queue[1:]
        typ, uuid = item[:2]
        if typ == 'collection':
            raw = f.fetch_url(collection_url % uuid)
            data = json.loads(raw)
            response = data['nyplAPI']['response']
            num_sub = int(response['numSubCollections'])
            num_items = int(response['numItems'])
            print(f'{uuid}: {num_sub} / {num_items}')
            if 'item' in response:
                item_list = as_list(response['item'])
                if len(item_list) < 10:
                    all_items += item_list
                    print(f'All items: {len(all_items)}')
                else:
                    # it's one above the leaves. Re-crawl it as items.
                    for i, start in enumerate(range(0, num_items, ITEMS_PER_PAGE)):
                        queue.append(('items', uuid, ITEMS_PER_PAGE, i))
            if 'collection' in response:
                collections_list = as_list(response['collection'])
                for collection in collections_list:
                    uuid = collection['uuid']
                    num_sub = int(collection['numSubCollections'])
                    num_items = int(collection['numItems'])
                    if num_sub == 0:
                        for i, start in enumerate(range(0, num_items, ITEMS_PER_PAGE)):
                            queue.append(('items', uuid, ITEMS_PER_PAGE, i))
                    else:
                        queue.append(('collection', uuid))
        elif typ == 'items':
            url = items_url % item[1:]
            raw = f.fetch_url(url)
            data = json.loads(raw)
            if 'item' not in response:
                # must have been a collection
                # print(data)
                continue
            response = data['nyplAPI']['response']
            all_items += as_list(response['item'])
            print(f'All items: {len(all_items)}')
