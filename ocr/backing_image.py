#!/usr/bin/env python

import json
import re
import sys

import record


def photo_id_to_backing_id(photo_id: str) -> str:
    return re.sub(r'f?(?:-[a-z])?$', 'b', photo_id, count=1)


def strip_photo_suffix(photo_id: str) -> str:
    return re.sub(r'-[a-z]*', '', photo_id)


if __name__ == '__main__':
    rs: list[record.Record] = json.load(open('nyc/records.json'))
    all_photo_ids = {r['id'] for r in rs}

    site_data = json.load(open('../oldnyc.github.io/data.json'))
    photo_ids_with_text = {
        strip_photo_suffix(photo['photo_id'])
        for photo in site_data['photos']
        if photo['text']
    }

    photo_ids = all_photo_ids.difference(photo_ids_with_text)

    for photo_id in photo_ids:
        back_id = None
        if 'f' in photo_id:
            back_id = photo_id_to_backing_id(photo_id)
        elif re.match(r'\d+$', photo_id):
            front = int(photo_id)
            back = front + 1
            if str(back) not in all_photo_ids:
                back_id = str(back)
        else:
            sys.stderr.write(f'Weird ID: {photo_id}\n')

        if back_id:
            url = f'http://images.nypl.org/?id={back_id}&t=w'
            print('ocr/images/%s.jpg\t%s' % (back_id, url))
