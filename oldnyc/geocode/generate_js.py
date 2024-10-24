#!/usr/bin/env python
"""Various output formats for generate-geocodes.py."""

import json
import sys
from collections import defaultdict
from json import encoder
from typing import Sequence

from oldnyc.geocode import record
from oldnyc.geocode.geocode_types import Locatable, Location
from oldnyc.item import Item

encoder.FLOAT_REPR = lambda o: format(o, ".6f")  # type: ignore


# could be tuple[Item, None, None] | tuple[Item, str, Location | Locatable]
LocatedRecord = tuple[Item, str | None, Location | Locatable | None]


def _generateJson(located_recs: Sequence[LocatedRecord], lat_lon_map: dict[str, str]):
    out = {}
    # "lat,lon" -> list of items
    ll_to_id: dict[str, list[Item]] = defaultdict(list)

    claimed_in_map = {}

    for r, _coder, location_data in located_recs:
        if not location_data:
            continue
        lat, lon = location_data.get("lat"), location_data.get("lon")
        assert lat is not None
        assert lon is not None
        ll_str = "%.6f,%.6f" % (lat, lon)
        if lat_lon_map and ll_str in lat_lon_map:
            claimed_in_map[ll_str] = True
            ll_str = lat_lon_map[ll_str]
        ll_to_id[ll_str].append(r)

    # print len(claimed_in_map)
    # print len(lat_lon_map)
    # assert len(claimed_in_map) == len(lat_lon_map)

    no_date = 0
    points = 0
    photos = 0
    for lat_lon, recs in ll_to_id.items():
        rec_dates = [(r, record.get_date_range(r.date or "")) for r in recs]
        # XXX the "if" filter here probably doesn't do anything
        sorted_recs = sorted(
            [rdr for rdr in rec_dates if rdr[1] and rdr[1][1]],
            key=lambda rdr: rdr[1][1],
        )
        no_date += len(recs) - len(sorted_recs)

        out_recs = []
        for r, date_range in sorted_recs:
            assert date_range[0]
            assert date_range[1]
            out_recs.append([date_range[0].year, date_range[1].year, r.id])

        if out_recs:
            points += 1
            photos += len(out_recs)
            out[lat_lon] = out_recs

    sys.stderr.write("Dropped w/ no date: %d\n" % no_date)
    sys.stderr.write("Unique lat/longs: %d\n" % points)
    sys.stderr.write("Total photographs: %d\n" % photos)

    return out


def printJson(located_recs: Sequence[LocatedRecord], lat_lon_map: dict[str, str]):
    data = _generateJson(located_recs, lat_lon_map)

    print("var lat_lons = ")
    print(json.dumps(data, sort_keys=True))


def printJsonNoYears(located_recs: list[LocatedRecord], lat_lon_map: dict[str, str]):
    data = _generateJson(located_recs, lat_lon_map)
    for k, v in data.items():
        data[k] = [x[2] for x in v]  # drop both year elements.

    print("var lat_lons = ")
    print(json.dumps(data, sort_keys=True))


def printLocationsJson(located_recs: list[LocatedRecord]):
    locs = {}
    for r, coder, location_data in located_recs:
        if location_data and "lat" in location_data and "lon" in location_data:
            lat = location_data["lat"]
            lon = location_data["lon"]
            locs[r.id] = [lat, lon]

    print(json.dumps(json.loads(json.dumps(locs), parse_float=lambda x: round(float(x), 6))))


def printRecordsJson(located_recs: list[LocatedRecord]):
    recs = []
    for r, coder, location_data in located_recs:
        rec = {
            "id": r.id,
            "folder": (r.address or "").replace("Folder: ", ""),
            "date": record.clean_date(r.date or ""),
            "title": record.clean_title(r.title),
            "description": r.back_text,
            "url": r.url,
            "extracted": {"date_range": [None, None]},
        }

        start, end = record.get_date_range(r.date or "")
        rec["extracted"]["date_range"][0] = "%04d-%02d-%02d" % (start.year, start.month, start.day)
        rec["extracted"]["date_range"][1] = "%04d-%02d-%02d" % (end.year, end.month, end.day)

        if coder and location_data:
            lat, lng = location_data.get("lat"), location_data.get("lon")
            if lat is not None and lng is not None:
                rec["extracted"]["latlon"] = (lat, lng)
                rec["extracted"]["located_str"] = location_data["address"]
                rec["extracted"]["technique"] = coder

        # TODO: remove this
        try:
            json.dumps(rec)
        except Exception as e:
            sys.stderr.write("%s\n" % rec)
            raise e

        recs.append(rec)
    # Net effect of this is to round lat/lngs to 6 decimals in the JSON, to match the
    # web site and the behavior of old version of this code.
    # https://stackoverflow.com/a/29066406/388951
    print(
        json.dumps(
            json.loads(json.dumps(recs), parse_float=lambda x: round(float(x), 6)),
            indent=2,
            sort_keys=True,
        )
    )


def printRecordsText(located_recs: list[LocatedRecord]):
    for r, coder, location_data in located_recs:
        date = record.clean_date(r.date or "")
        title = record.clean_title(r.title)
        folder = r.address
        if folder:
            folder = record.clean_folder(folder)

        if location_data:
            lat, lng = location_data.get("lat"), location_data.get("lon")
            loc = (str((lat, lng)) or "") + "\t" + location_data["address"]
        else:
            loc = "n/a\tn/a"

        print("\t".join([r.id, date, folder or "", title, r.url, coder or "failed", loc]))


def printIdLocation(located_recs: list[LocatedRecord]):
    for r, coder, location_data in located_recs:
        if location_data:
            lat, lng = location_data.get("lat"), location_data.get("lon")
            loc = (str((lat, lng)) or "") + "\t" + location_data["address"]
        else:
            loc = "n/a\tn/a"

        print("\t".join([r.id, coder or "failed", loc]))


def printLocations(located_recs: list[LocatedRecord]):
    locs = defaultdict(int)
    for _r, _coder, location_data in located_recs:
        if location_data and "lat" in location_data and "lon" in location_data:
            lat = location_data["lat"]
            lon = location_data["lon"]
            locs["%.6f,%.6f" % (lat, lon)] += 1

    for ll, count in locs.items():
        print("%d\t%s" % (count, ll))


def output_geojson(located_recs: list[LocatedRecord], all_recs: list[Item]):
    features = []
    id_to_loc = {rec[0].id: rec for rec in located_recs}
    for r in all_recs:
        _, coder, location_data = id_to_loc[r.id]
        feature = {
            "id": r.id,
            "type": "Feature",
            "geometry": (
                {
                    "type": "Point",
                    "coordinates": [location_data["lon"], location_data["lat"]],  # type: ignore
                }
                if location_data
                else None
            ),
            "properties": {
                "title": r.title,
                "date": r.date,
                "geocode": (
                    {
                        "technique": coder,
                        "lat": location_data["lat"],  # type: ignore
                        "lng": location_data["lon"],  # type: ignore
                        **location_data,
                    }
                    if location_data
                    else None
                ),
                "image": {
                    "url": f"http://images.nypl.org/?id={r.id}&t=w",
                    "thumb_url": f"http://images.nypl.org/?id={r.id}&t=w",
                },
                "url": r.url,
                "nypl_fields": {"alt_title": r.alt_title, "address": r.address},
            },
        }
        features.append(feature)

    print(
        json.dumps(
            {"type": "FeatureCollection", "features": features},
            indent=2,
            sort_keys=True,
        )
    )
