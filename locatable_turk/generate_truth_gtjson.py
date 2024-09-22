#!/usr/bin/env python3
"""Generate truth GTJSON from the localturk CSV output.

See:
https://docs.google.com/spreadsheets/d/1AZ_X4YFPJF9-KdRxjdiDJhRF5z6tAd3fBBaAXBZLNHE/edit
"""

from collections import defaultdict
import json
import csv


def merge_entries(entries):
    """We have more than one source of truth data for a single entry. Merge them!

    entries are (date, geometry, row) tuples.
    """
    # If only one source thinks the record is locatable, use that.
    located = [e for e in entries if e[1]]

    rows_with_notes = [e[2] for e in entries if e[2]['user_notes']]
    if len(rows_with_notes) == 0:
        note = ''
    elif len(rows_with_notes) == 1:
        note = rows_with_notes[0]['user_notes']
    else:
        note = '\n'.join('%s: %s' % (row['source'], row['user_notes']) for row in rows_with_notes)

    if len(located) == 0:
        entries[0][2]['user_notes'] = note
        return entries[0]

    elif len(located) == 1:
        located[0][2]['user_notes'] = note
        return located[0]

    # We've got multiple locations. Average them?
    avg_lat = sum(float(e[2]['Lat']) for e in located) / len(located)
    avg_lng = sum(float(e[2]['Lng']) for e in located) / len(located)
    geometry = {
        'type': 'Point',
        'coordinates': [avg_lng, avg_lat]
    }

    located[0][2]['user_notes'] = note
    return (located[0][0], geometry, located[0][2])


if __name__ == '__main__':
    id_to_data = defaultdict(list)

    for row in csv.DictReader(open('locatable-turk/truth-combined.csv')):
        id_ = row['uniqueID']
        is_locatable = row['geolocatable'] == 'Locatable'

        geometry = None
        if is_locatable:
            (lng, lat) = (float(row['Lng']), float(row['Lat']))
            geometry = {
                'type': 'Point',
                'coordinates': [lng, lat]
            }

        date = None
        if row['datable'] == 'yes':
            start = row['date_start']
            end = row['date_end']
            if start and not end:
                date = start
            elif end and not start:
                # TODO(danvk): this is kind of a lie; https://stackoverflow.com/q/48696238/388951
                date = end
            elif start and end:
                if start == end:
                    date = start
                else:
                    date = '%s/%s' % (start, end)
            else:
                raise ValueError('Empty start/end for %s' % id_)

        id_to_data[id_].append((date, geometry, row))

    features = []
    for id_, entries in id_to_data.items():
        if len(entries) == 1:
            entry = entries[0]
        else:
            entry = merge_entries(entries)

        date, geometry, row = entry

        features.append({
            'type': 'Feature',
            'geometry': geometry,
            'id': id_,
            'properties': {
                'date': date,
                'title': row['title'],
                'geocoding_notes': row['user_notes'],
                'source': row['source']
            }
        })

    print(json.dumps({
        'type': 'FeatureCollection',
        'features': features
    }))
