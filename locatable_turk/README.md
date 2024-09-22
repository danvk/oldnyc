# Manual geolocation and dating

To run this, you'll need [localturk][], [jq][] and [csvkit][]:

    brew install coreutils csvkit jq
    npm install -g localturk

First pick out some random IDs:

    jq .uniqueID images.ndjson | sed 's/"//g' | gshuf | grep -v null | head -500 > random-500-ids.txt

Then fetch them, parse the results and attach parents:

    ./fetch_archive_records.py random-500-ids.txt
    ./parse_records.py random-500-ids.txt locatable-turk/random-500.ndjson
    ./attach_small_parents.py locatable-turk/random-500.ndjson locatable-turk/random-500+parents.ndjson

Finally, convert to CSV and run localturk!

    cd locatable-turk
    in2csv --format ndjson random-500+parents.ndjson > random-500.csv
    localturk template.html random-500.csv out.csv

If you want to generate a new permutation of the records, run:

    gshuf random-500+parents.ndjson > /tmp/random.ndjson
    in2csv --format ndjson /tmp/random.ndjson > random-500.csv

[localturk]: https://github.com/danvk/localturk
[csvkit]: https://csvkit.readthedocs.io/en/1.0.2/
[jq]: https://stedolan.github.io/jq/
