# Manual geolocation and dating

To run this, you'll need [localturk][] and [csvkit][]:

    brew install jq
    npm install -g localturk

Here are some relevant commands from my CLI history:

```bash
gshuf data/images.ndjson | head -500 | jq -r .id > data/geocode/random500-ids.txt
poetry run oldnyc/geocode/geocode.py --images_ndjson data/images.ndjson --output_format geojson --ids_filter data/geocode/random500-ids.txt  --geocode > /tmp/images.geojson
poetry run oldnyc/geocode/truth/make_localturk_csv.py data/geocode/random500-ids.txt /tmp/images.geojson data/geocode/random500.csv
localturk -r --var GOOGLE_MAPS_API_KEY="..." template.html random500.csv out.csv
poetry run oldnyc/geocode/truth/fix_truth.py data/geocode/out.csv data/geocode/truth.csv
poetry run oldnyc/geocode/truth/generate_truth_gtjson.py > data/geocode/truth.geojson
jq -r '.features[].id' data/geocode/truth.geojson > data/geocode/truth-ids.txt
```

To calculate metrics:

```bash
poetry run oldnyc/geocode/geocode.py --images_ndjson data/images.ndjson --ids_filter data/geocode/truth-ids.txt --output_format geojson --geocode > data/geocode/site.geojson
poetry run oldnyc/geocode/calculate_metrics.py --truth_data data/geocode/truth.geojson --computed_data data/geocode/site.geojson
```

[localturk]: https://github.com/danvk/localturk
[csvkit]: https://csvkit.readthedocs.io/en/1.0.2/
