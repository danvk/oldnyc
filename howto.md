# How to do various things for Old NYC

The web site and static data live over in https://github.com/oldnyc/oldnyc.github.io.

If any of these workflows aren't working, check `e2etest.yml` to see if there's a more
up-to-date version.

## Setup

Set up the Python environment:

    poetry install

## Update the data

Data (lat/lon→image lists, image metadata), is hosted on GitHub pages. To
update this, run something like this sequence:

```bash
cd ..
git clone https://github.com/oldnyc/oldnyc.github.io.git
cd ../oldnyc
poetry run oldnyc/site/generate_static_site.py
cd ../oldnyc.github.io
git add .
git commit -a -m 'Update site'
git push
```

## Iterate on geocoding

It's easiest to do this by iterating on the `images.ndjson` file, which has one
entry per milstein card, rather than one entry per photo.

    poetry run oldnyc/geocode/geocode.py --coders milstein --images_ndjson data/images.ndjson --output_format geojson --geocode > /tmp/images.geojson

This will print out lots of information about incorrect geocodes and eventually print something like:

    25574 milstein
    25574 (total)

This is out of 43363 total records in the Milstein collection.

By default, this only uses the local "geocache"--it doesn't fetch any geocodes
from Google Maps. If you want to do that, add --use_network:

    poetry run oldnyc/geocode/geocode.py --images_ndjson data/images.ndjson --output_format geojson --geocode --use_network > /tmp/images.geojson

If you want to determine per-borough geocoding coverage, run

    poetry run oldnyc/analysis/coverage-by-borough.py /tmp/records.json

## Regenerate geocodes for the viewer (nyc-lat-lons-ny.js)

Start by unpacking the geocache. This will speed up geocoding and help ensure stable results:

    tar -xzf geocache.tgz

To get new geocodes into the frontend, you need to geocode `photos.ndjson`
(see below for how to generate this). Do so with:

    poetry run oldnyc/geocode/geocode.py --images_ndjson data/photos.ndjson --lat_lon_map data/lat-lon-map.txt --output_format lat-lon-to-ids.json --geocode > data/lat-lon-to-ids.json

The lat-lon-map.txt file can be generated via:

    poetry run oldnyc/geocode/geocode.py --images_ndjson data/images.ndjson --output_format locations.txt --geocode > data/locations.txt
    poetry run oldnyc/geocode/cluster.py locations.txt > data/lat-lon-map.txt

To update the geocache:

    rm geocache.tgz
    tar -czf geocache.tgz geocache

If you've added new photos to the map, you'll need to add them to the "self-hosted" images list, see "Adding images" below.

## Generate photos.ndjson

`photos.ndjson` is like `images.ndjson`, but it duplicates each record across all its photos.
(There are potentially several photos on the Milstein card for each record.)

    poetry run oldnyc/crop/records_to_photos.py data/images.ndjson data/crops.ndjson data/photos.ndjson

## Generate crops.ndjson

    # produces detected-photos.ndjson
    poetry run oldnyc/crop/find_pictures.py path/to/images/*.jpg > /tmp/detected-photos.ndjson
    # produces cropped images and crops.ndjson
    poetry run oldnyc/crop/extract_photos.py outputdir /tmp/detected-photos.ndjson > data/crops.ndjson

## Generate extended grid data

This has no inputs and outputs `grid/intersections.csv`:

    poetry run grid/gold.py

(Note that this does not work as of 2024 due to Google Maps geocoding changes.)

## Generate images.ndjson from CSV

Sources of data:

- `milstein.csv`, the original CSV file that Matt K gave me in 2013.
- `Milstein_data_for_DV_2.csv`, an update from 2024.
- `mods-details.json`, which includes data from the NYPL API's `/mods` and `/item_details` endpoints.
- ...

To collect these into an `images.ndjson` file, run:

    poetry run oldnyc/ingest/ingest.py

## Adding images

The NYPL hosts most of the imagery for OldNYC in an S3 bucket that's served at oldnyc-assets.nypl.org.

This bucket was populated in 2015 and hasn't been touched since. So new images need to be handled differently. The web UI needs to know the size of each image to render properly. So the process is to fetch thumbnails of the new images and determine their size.

    poetry run ./oldnyc/site/missing_images.py > /tmp/images-to-crawl.txt
    poetry run oldnyc/url_fetcher.py --output-dir ~/Documents/oldnyc /tmp/images-to-crawl.txt
    poetry run oldnyc/ingest/extract_sizes.py --file <(cut -f2 /tmp/images-to-crawl.txt | perl -pe 's,^,/Users/danvk/Documents/oldnyc/,') > data/self-hosted-sizes.txt
