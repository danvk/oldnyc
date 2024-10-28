# Manual geolocation and dating

To run this, you'll need [localturk][], [jq][] and [csvkit][]:

    brew install coreutils csvkit jq
    npm install -g localturk

Here are some relevant commands from my CLI history:

```bash
./generate-geocodes.py --images_ndjson data/images.ndjson --output_format id-location.json --geocode > data/geocode/id-to-location.json
./data/geocode/json_to_csv.py <(gshuf data/images.ndjson | head -500) /tmp/id-to-location.json data/geocode/random500.csv
localturk -r --var GOOGLE_MAPS_API_KEY="..." template.html random500.csv out.csv
python data/geocode/fix_truth.py data/geocode/out.csv data/geocode/truth.csv
csvcut -c id data/geocode/truth.csv| sed 1d > data/geocode/truth-ids.txt
./data/geocode/generate_truth_gtjson.py | jq . > data/geocode/truth.geojson
```

[localturk]: https://github.com/danvk/localturk
[csvkit]: https://csvkit.readthedocs.io/en/1.0.2/
[jq]: https://stedolan.github.io/jq/
