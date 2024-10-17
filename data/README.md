# OldNYC Ddata

All data comes together into a single `images.ndjson` file (see oldnyc/ingest).

Input data (sources of truth) live in `data/originals`. Files in the top-level
`data` directory are derived from those and other sources.

Inputs:

- `data/originals/milstein.csv`: the vintage 2013 CSV file from the NYPL that started it all
  - Contains image ID (typically starts with "7" and ends with "f")
  - Contains title, alt_title
  - Contains dates
  - Contains creator
  - Contains source (corresponds to subcollection)
  - Contains Address and Full Address (unclear provenance)
- `data/originals/Milstein_data_for_DV.csv`: the 2024 update to the CSV
  - Contains image ID (with a capital "F" this time)
  - Contains title (which may have changed since 2013)
  - Contains two UUIDs, which can be used to construct a Digital Collections (DC) URL
  - Contains a capture count, which can be used to determine if an image has backing text.
  - Contains various "subjects", which sometimes contain location information.
- `data.json`: contains OCR text from 2015 (Ocropy) plus manual fixes
- `gpt-text.json`: contains OCR text from 2024 via OpenAI

...
