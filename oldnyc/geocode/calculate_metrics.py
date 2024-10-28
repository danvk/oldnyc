#!/usr/bin/env python3
"""Calculate metrics between two GTJSON files.

This will print row-by-row metrics and overall summary statistics. These can be copy/pasted into
a spreadsheet for further analysis.

Taxonomy of errors:

Geocodes
    - Missing a location
    - Have a location where there should be none
    - Location is far (>250m?) from true location. Bullseye = within 25m?
"""

import argparse
import csv
import json
import sys

from haversine import haversine


def _coord_to_str(coord):
    # Returns (lat, lng) for easy pasting into Google Maps
    return "%.6f,%.6f" % (coord[1], coord[0]) if coord else "None"


def diff_geocode(truth_coord, computed_coord):
    """Compare two coordinates. Returns (match?, reason for mismatch, d_km).

    Coords are (lng, lat). Either may be None.
    """
    if _coord_to_str(truth_coord) == _coord_to_str(computed_coord):
        return (True, "", "0")
    if computed_coord is None:
        return (False, "Missing geocode", "")
    if truth_coord is None:
        return (False, "Should be missing geocode", "")
    distance_km = haversine(truth_coord, computed_coord)
    if distance_km > 0.25:
        return (False, "Too far: %.3f km" % distance_km, f"{distance_km:.3f}")
    return (True, "", f"{distance_km:.3f}")


def tally_stats(truth_features, computed_features):
    """Print row-by-row results and overall metrics."""
    id_to_truth_feature = {f["id"]: f for f in truth_features}

    num_geocodable = 0
    num_geocoded_correct = 0
    num_geocoded_incorrect = 0
    num_geocoded = 0

    out = csv.writer(sys.stdout, delimiter="\t")
    out.writerow(
        [
            "id",
            "url",
            "title",
            "computed location",
            "true location",
            "d (km)",
            "incorrectly located",
            "location match",
            "location reason",
            "geocode technique",
            "location string",
            "truth source",
            "notes",
        ]
    )
    for feature in computed_features:
        id_ = feature["id"]
        props = feature["properties"]
        truth_feature = id_to_truth_feature.get(id_)
        if not truth_feature:
            continue

        true_coords = truth_feature["geometry"] and truth_feature["geometry"]["coordinates"]
        computed_coords = feature["geometry"] and feature["geometry"]["coordinates"]
        if true_coords:
            num_geocodable += 1
        if computed_coords:
            num_geocoded += 1
        (geocode_match, geocode_reason, d_km) = diff_geocode(true_coords, computed_coords)

        if geocode_match and true_coords:
            num_geocoded_correct += 1
        incorrectly_located = computed_coords and not geocode_match
        if incorrectly_located:
            num_geocoded_incorrect += 1

        search_term = ""
        technique = ""
        if computed_coords:
            search_term = props["geocode"]["source"]
            technique = props["geocode"]["technique"]

        out.writerow(
            [
                str(x)
                for x in (
                    id_,
                    props["url"],
                    props["title"],
                    _coord_to_str(computed_coords),
                    _coord_to_str(true_coords),
                    d_km,
                    "TRUE" if incorrectly_located else "FALSE",
                    geocode_match,
                    geocode_reason,
                    technique,
                    search_term,
                    truth_feature["properties"]["source"],
                    truth_feature["properties"].get("geocoding_notes", ""),
                )
            ]
        )

    print(
        """
Results:
  Geocodes
    %3d / %3d = %.2f%% of locatable images correctly located.
    %3d / %3d = %.2f%% incorrectly located.
"""
        % (
            num_geocoded_correct,
            num_geocodable,
            100.0 * num_geocoded_correct / num_geocodable,
            num_geocoded_incorrect,
            num_geocoded,
            100.0 * num_geocoded_incorrect / num_geocoded,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Comparse geojson derived from geocoding against truth data")
    parser.add_argument(
        "--truth_data",
        type=str,
        help=".gtjson files containing truth data",
        default="data/truth.gtjson",
    )
    parser.add_argument(
        "--computed_data",
        type=str,
        help="result of generate_geojson.py from geocoded images",
        default="data/images.geojson",
    )
    args = parser.parse_args()

    truth_features = json.load(open(args.truth_data))["features"]
    computed_features = json.load(open(args.computed_data))["features"]

    tally_stats(truth_features, computed_features)
