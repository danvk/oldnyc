#!/usr/bin/env python3
"""Diffs a before and after geojson producing deleted, after, changed and unchanged geojson files.

This can be used to estimate what locations in the before input have been corrected in the after
input. In order to estimate the correctness of features one can assume that features with location
changes in the after geojson are corrected and any features that haven't changed location to
remain incorrect. Note: this would label deleted features as incorrect.

 If the number of features in either geojson are too numerous, you can restrict the
features used for the diffing by passing the sample_set flag a pipe delimited set of ids as a
restriction. For example, this would be useful if a second geojson is constructed over a subset of
ids that are suspected of being incorrect.

Output .geojson files:
    - dropped: features from the before file that no longer appear in the after
    - added: features from the before file that are in the after file, but in the before
    - changed: features that appear in both files, but are in different locations
    - unchanged: features that appear in both files, and are in the same location
"""

import argparse
import json
import math
import random
from typing import Optional, Sequence

from haversine import haversine


def features_to_geojson_file(features, filename):
    with open(filename, "w") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)


def calculate_distance_delta_for_image_id(a, b):
    assert a["type"] == "Point"
    assert b["type"] == "Point"
    (a_lng, a_lat) = a["coordinates"]
    (b_lng, b_lat) = b["coordinates"]
    d_meters = haversine((a_lat, a_lng), (b_lat, b_lng)) * 1000
    return d_meters


def is_geometry_mismatch(a, b):
    """Has the geometry type changed?"""
    return (a is None) != (b is None) or a["type"] != b["type"]


def diff_geojson(
    before_file: str,
    after_file: str,
    added_file: str,
    dropped_file: str,
    changed_file: str,
    unchanged_file: str,
    sample_set: Optional[Sequence[str]],
    num_samples: int,
):
    before = json.load(open(before_file))["features"]
    old = {x["id"]: x for x in before}
    after = json.load(open(after_file))["features"]
    new = {x["id"]: x for x in after}
    old_ids = {x["id"] for x in before}
    new_ids = {x["id"] for x in after}
    if sample_set:
        old_ids = old_ids.intersection(sample_set)
        new_ids = new_ids.intersection(sample_set)

    dropped_ids = old_ids.difference(new_ids)
    added_ids = new_ids.difference(old_ids)
    changed_ids = []
    dropped_geometry_ids = []
    added_geometry_ids = []
    for k in new_ids.intersection(old_ids):
        a = old[k]["geometry"]
        b = new[k]["geometry"]
        if a is None and b is None:
            continue
        elif a is None and b is not None:
            added_geometry_ids.append(k)
        elif b is None and a is not None:
            dropped_geometry_ids.append(k)
        elif is_geometry_mismatch(a, b) or calculate_distance_delta_for_image_id(a, b) > 25:
            changed_ids.append(k)

    # we estimate that all reported images who have not changed are unchanged
    unchanged_ids = (
        old_ids.difference(changed_ids)
        .difference(dropped_ids)
        .difference(dropped_geometry_ids)
        .difference(added_geometry_ids)
    )

    dropped_features = [old[i] for i in dropped_ids]
    added_features = [new[i] for i in added_ids]
    changed_features = [new[i] for i in changed_ids]
    unchanged_features = [old[i] for i in unchanged_ids]

    features_to_geojson_file(dropped_features, dropped_file)
    features_to_geojson_file(added_features, added_file)
    features_to_geojson_file(changed_features, changed_file)
    features_to_geojson_file(unchanged_features, unchanged_file)

    print(f"""
 Before: {len(old_ids):,}
  After: {len(new_ids):,}

  Added: {len(added_ids):,}
Dropped: {len(dropped_ids):,}
Changed: {len(changed_ids):,}
  +geom: {len(added_geometry_ids):,}
  -geom: {len(dropped_geometry_ids):,}
""")

    if added_ids and num_samples:
        print("\nSample of additions:")
        add_samples = min(num_samples, len(added_ids))
        for k in random.sample([*added_ids], add_samples):
            props = new[k]["properties"]
            b = props["geocode"]
            title = (
                b.get("original_title")
                or b.get("title")
                or props.get("title")
                or "original title not found"
            )
            print(f" {k:6}: {title}")
            print(f'   + {b.get("lat"):.6f},{b.get("lng"):.6f} {b.get("technique")}')

    if dropped_ids and num_samples:
        print("\nSample of dropped:")
        drop_samples = min(num_samples, len(dropped_ids))
        for k in random.sample([*dropped_ids], drop_samples):
            a = old[k]["properties"]["geocode"]
            print(f' {k:6}: {a.get("original_title", "original title not found")}')
            print(f'   - {a.get("lat"):.6f},{a.get("lng"):.6f} {a.get("technique")}')

    if changed_ids and num_samples:
        print("\nSample of changes:")
        changed_samples = min(num_samples, len(changed_ids))
        for k in random.sample([*changed_ids], changed_samples):
            a = old[k]["properties"]["geocode"]
            b = new[k]["properties"]["geocode"]
            a_lat = a.get("lat")
            a_lng = a.get("lng")
            b_lat = b.get("lat")
            b_lng = b.get("lng")
            d_meters = haversine((a_lat, a_lng), (b_lat, b_lng)) * 1000

            print(f' {k:6}: {a.get("original_title", "original title not found")}')
            print(f'   - {a_lat:.6f},{a_lng:.6f} {a.get("technique")}')
            print(f'   + {b_lat:.6f},{b_lng:.6f} {b.get("technique")}')
            print(f"     Moved {d_meters:0,.0f} meters")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Analyze the differences between two sets of geocodes.")
    parser.add_argument("before", help="Path to geojson before", type=str)
    parser.add_argument("after", help="Path to geojson after", type=str)
    parser.add_argument(
        "--dropped",
        type=str,
        default="/tmp/dropped.geojson",
        help="Path to save features that appeared in the before geojson but not in"
        "the after geojson",
    )
    parser.add_argument(
        "--added",
        type=str,
        default="/tmp/added.geojson",
        help="Path to save features that appeared in the after geojson but not in"
        "the before geojson",
    )
    parser.add_argument(
        "--changed",
        type=str,
        default="/tmp/changed.geojson",
        help="Path to save features that have different coordinates",
    )
    parser.add_argument(
        "--unchanged",
        type=str,
        default="/tmp/unchanged.geojson",
        help="Path to save features whose locations remain unchanged",
    )
    parser.add_argument(
        "--sample_set",
        type=str,
        help="Pipe delimited image id, representing a set of image ids to diff",
        default=None,
    )
    parser.add_argument(
        "--verbose_metrics",
        type=bool,
        default=True,
        help="If True, will print more verbose metrics",
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        help="Number of examples of each type (add, drop, change) to show.",
        default=0,
    )
    args = parser.parse_args()

    sample_set = args.sample_set.split("|") if args.sample_set else None
    diff_geojson(
        args.before,
        args.after,
        args.added,
        args.dropped,
        args.changed,
        args.unchanged,
        sample_set,
        args.num_samples,
    )
