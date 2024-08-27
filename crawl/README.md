# NYPL API Crawl

Goal is to get additional information about photos that's only available via
the [NYPL API], not the original CSV file I received via email in 2013.

To generate `nyc-records.extended.json`:

```
# Fetch all root (non-parented) UUIDs from the NYPL
./crawl/roots.py
# Figure out which of these are in the Milstein division
./crawl/find_milstein_collections.py
# Recursively crawl collections and subcollections for "items" and "captures"
./crawl/crawl_collections.py
# Combine CSV and crawl data to build extended records.
./crawl/build_extended_records.py
```

Stats:

- 43363 records
- 40742 are matched with a UUID
- 34509 have an associated `item` from the NYPL API (with MODS data)
- 19666 have an associated `capture` (which contains a title and UUID)
- 39389 have either an `item` or a `capture`
- 25418 have backing text from OCR or user submissions.

[NYPL API]: https://api.repo.nypl.org/
