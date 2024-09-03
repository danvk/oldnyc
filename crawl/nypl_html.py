"""Assorted tools for parsing NYPL HTML."""

import re
import json
from bs4 import BeautifulSoup
from bs4.element import NavigableString

# TODO: define TypedDicts for all of these

def extract_results(results_html: str):
    """Extract data from a search results page."""
    soup = BeautifulSoup(results_html, 'html.parser')
    return [
        {
            'uuid': div.a['href'].split('/')[-1],
            'image_url': (src := div.img['src']),
            'title': div.a['title'],
            'has_multiple': not not div.select('span.multiple'),
            'photo_id': re.search(r'id=([0-9fbFB]+)&', src).group(1).lower()
        }
        for div in soup.select('div.item')
    ]


def walk(data, topic=None) -> list[(str, str | None, str)]:
    """Walk the dt/dd mess in the "Item Data" section of an NYPL item page."""
    extracts = []
    for el in data.contents:
        if isinstance(el, NavigableString) and str(el).strip() and topic:
            extracts.append((topic, None, str(el).strip()))
        elif el.name == 'dt':
            topic = el.string
        elif el.name == 'dd':
            if el.dd:
                extracts += walk(el, topic)
            else:
                txt = str(el.text).strip()
                parts = txt.split(':')
                if len(parts) >= 2:
                    (k, v) = txt.split(':', 2)
                    extracts.append((topic, k.strip(), v.strip()))
                elif txt:
                    extracts.append((topic, None, txt))
    return extracts


field_map = {
    ('Title', 'Additional title'): (1, 'alt_title'),
    ('Dates / Origin', 'Place'): (1, 'place'),
    ('Dates / Origin', 'Date Created'): (1, 'date_created'),
    ('Topics', None): (0, 'topics'),
    ('Identifiers', 'Universal Unique Identifier (UUID)'): (1, 'uuid'),
    ('Identifiers', 'RLIN/OCLC'): (1, 'rlin_oclc'),
    ('Identifiers', 'NYPL catalog ID (B-number)'): (1, 'bnumber'),
    ('Genres', None): (1, 'genre'),
    ('Type of Resource', None): (1, 'resource_type'),
}


def extract_item(item_html: str):
    """Extract data for an item page."""
    soup = BeautifulSoup(item_html, 'html.parser')
    item = json.loads(soup.select('[data-item]')[0]['data-item'])
    items = [json.loads(el['data-items']) for el in soup.select('[data-items]')]

    meta = {}
    data = soup.select('#item-content-data')[0]
    for topic, subtopic, value in walk(data):
        key = (topic, subtopic)
        target = field_map.get(key)
        if not target:
            continue
        n, fieldname = target
        if n == 1:
            assert fieldname not in meta
            meta[fieldname] = value
        elif n == 0:
            meta.setdefault(fieldname, [])
            meta[fieldname].append(value)
        else:
            raise ValueError(f'{key=}, {target=}')

    siblings = items[0]
    sibling = siblings[1] if len(siblings) == 2 and siblings[0]['id'] == item['id'] else None
    return {
        'id': item['image_id'],
        'uuid': item['id'],
        'item': item,
        'sibling': sibling,
        # 'items': items[0],
        'meta': meta
    }
