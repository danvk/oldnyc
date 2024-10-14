# How to do various things for Old NYC

The web site and static data live over in https://github.com/oldnyc/oldnyc.github.io.

## Setup

Set up the Python environment:

```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## Update the data

Data (lat/lon→image lists, image metadata), is hosted on GitHub pages. To
update this, run something like this sequence:

```bash
cd ..
git clone https://github.com/oldnyc/oldnyc.github.io.git
cd ../oldnyc
./generate_static_site.py
cd ../oldnyc.github.io
git add .
git commit -a -m 'Update site'
git push
```

## Iterate on geocoding

It's easiest to do this by iterating on the `images.ndjson` file, which has one
entry per milstein card, rather than one entry per photo.

    ./generate-geocodes.py --coders milstein --images_ndjson data/images.ndjson --output_format records.js --geocode > /tmp/records.json

This will print out lots of information about incorrect geocodes and eventually print something like:

    25574 milstein
    25574 (total)

This is out of 43363 total records in the Milstein collection.

By default, this only uses the local "geocache"--it doesn't fetch any geocodes
from Google Maps. If you want to do that, add --use_network:

    ./generate-geocodes.py --images_ndjson data/images.ndjson --output_format records.js --geocode --use_network > /tmp/records.json

If you want to determine per-borough geocoding coverage, run

    ./nyc/coverage-by-borough /tmp/records.json

## Regenerate geocodes for the viewer (nyc-lat-lons-ny.js)

Start by unpacking the geocache. This will speed up geocoding and help ensure stable results:

    tar -xzf geocache.tgz

To get new geocodes into the frontend, you need to geocode `photos.ndjson`
(see below for how to generate this). Do so with:

    ./generate-geocodes.py --images_ndjson data/photos.ndjson --lat_lon_map lat-lon-map.txt --output_format lat-lons-ny.js --geocode > viewer/static/js/nyc-lat-lons-ny.js

The lat-lon-map.txt file can be generated via:

    ./generate-geocodes.py --images_ndjson data/images.ndjson --output_format locations.txt --geocode > locations.txt
    ./cluster-locations.py locations.txt > lat-lon-map.txt

## Generate photos.ndjson

`photos.ndjson` is like `images.ndjson`, but it duplicates each record across all its photos.
(There are potentially several photos on the Milstein card for each record.)

```bash
./nyc/crops-to-json.py nyc/crops.txt > /tmp/crops.json
./nyc/records_to_photos.py data/images.ndjson /tmp/crops.json data/photos.ndjson
```

To update the geocache:

    rm geocache.tgz
    tar -czf geocache.tgz geocache

## Generate crops.txt

...

## Generate images.ndjson from CSV

Sources of data:

- `milstein.csv`, the original CSV file that Matt K gave me in 2013.
- `Milstein_data_for_DV_2.csv`, an update from 2024.
- `mods-details.json`, which includes data from the NYPL API's `/mods` and `/item_details` endpoints.

To collect these into an `images.ndjson` file, run:

    ./data/ingest.py
