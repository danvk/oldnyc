# Subjects geocoding

NYPL records have a `subjects` field that looks like this:

```json
{
    "name": [],
    "temporal": [],
    "geographic": [
      "Jackie Robinson Park (New York, N.Y.)",
      "Manhattan (New York, N.Y.)",
      "New York",
      "New York (N.Y.)",
      "New York (State)"
    ],
    "topic": [
      "Parks",
      "Playgrounds"
    ]
}
```

Some of the `geographic` entries are too broad to be interesting, but Jackie Robinson Park is specific enough to give us a location. The code in this directory explores `subject` as a source of geocodes.
