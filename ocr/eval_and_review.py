#!/usr/bin/env python
"""Evaluate the differences between two OCR files and output JS for manual review.

Input is two JSON files mapping back ID -> text (base and experiment).
Outputs some stats and fills in ocr/feedback/review/changes.js
"""

import json
import sys

from ocr.tess.evaluate_ocr import score_for_pair
from record import Record


if __name__ == '__main__':
    (base_file, exp_file) = sys.argv[1:]

    base: dict[str, str] = json.load(open(base_file))
    exp: dict[str, str] = json.load(open(exp_file))

    records: list[Record] = json.load(open('nyc/records.json'))
    id_to_record = {r['id']: r for r in records}
    front_to_back = {r['id']: r['back_id'] for r in records if r['back_id']}
    site_data = json.load(open('../oldnyc.github.io/data.json'))
    back_to_front = {}
    for r in site_data['photos']:
        id = r['photo_id']
        photo_id = id.split('-')[0]
        back_id = front_to_back.get(photo_id)
        if back_id:
            back_to_front[back_id] = id

    scores = []
    changes = []
    for id, exp_text in exp.items():
        base_text = base[id]
        (score, distance) = score_for_pair(base_text, exp_text)
        scores.append(score)
        changes.append({
            'photo_id': back_to_front[id],  # should be back ID
            'before': base_text,
            'after': exp_text,
            'metadata': {
                'cookie': 'eval',
                'len_base': len(base_text),
                'len_exp': len(exp_text),
                'distance': distance,
                'score': score,
                'back_id': id,
                'record': id_to_record[back_to_front[id].split('-')[0]]
            }
        })

    changes.sort(key=lambda r: r['metadata']['score'])
    for change in changes:
        # id = change['photo_id']
        back_id = change['metadata']['back_id']
        score = change['metadata']['score']
        distance = change['metadata']['distance']
        len_base = change['metadata']['len_base']
        len_exp = change['metadata']['len_exp']
        print('%s\t%.3f\t%4d\t%d\t%d' % (back_id, score, distance, len_base, len_exp))

    mean = sum(scores) / len(scores)
    print('Average: %.3f' % mean)

    open('ocr/feedback/review/changes.js', 'w').write('var changes = %s;' %
        json.dumps(changes, indent=2))