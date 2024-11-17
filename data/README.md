# OldNYC Ddata

All data comes together into a single `images.ndjson` file (see oldnyc/ingest).

Input data (sources of truth) live in `data/originals`. Files in the top-level
`data` directory are derived from those and other sources.

Inputs:

- `data/originals/Milstein_data_for_DV.csv`: the 2024 update to the CSV
  - Contains image ID (with a capital "F" this time)
  - Contains title (which may have changed since 2013)
  - Contains two UUIDs, which can be used to construct a Digital Collections (DC) URL
  - Contains a capture count, which can be used to determine if an image has backing text.
  - Contains various "subjects", which sometimes contain location information.
- `site-ocr-2024.json`: contains OCR text from 2015 (Ocropy) plus manual fixes
- `gpt-text.json`: contains OCR text from 2024 via OpenAI
- `osm-roads.json`: Filtered street network data from OSM Overpass API.

TODO:

- Document provenance for all files.

## Repro instructions

### osm-roads.json

Run `data/nyc-named-roads.overpass-query.txt` through the Overpass API. This will produce a big JSON file that needs to be filtered. You can do this with:

    poetry run python oldnyc/geocode/osm/filter_overpass_json.py /tmp/results.json > data/osm-roads.json
