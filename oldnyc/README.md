# OldNYC directory structure

All Python code should live under the `oldnyc` directory. There shouldn't be any
data files in this directory (those live in `data`).

The intention is for the following subdirectories to be mostly independent of one
anther. Code shared across many subdirectories (e.g. `Item`) can live at the top
level.

- ingest: code used to produce `images.ndjson`
- crop: finding and extracting photos and text from larger images
- geocode: locating items
- ocr: transcribing text from the ocrbacks
- feedback: processing user feedback
- site: generating the OldNYC site in oldnyc.github.io
- analysis: code that is not part of the pipeline, including all notebooks.
