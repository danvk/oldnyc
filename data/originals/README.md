# Data Sources

Files in this folder are "originals"—not derived from some other data source.

- `data/originals/milstein.csv`: the vintage 2013 CSV file from the NYPL that started it all
- `data/originals/Milstein_data_for_DV.csv`: the 2024 update to the CSV
- Street listings
  - `manhattan-streets.txt`: https://geographic.org/streetview/usa/ny/new_york/new_york.html
  - `brooklyn-streets.txt`: https://geographic.org/streetview/usa/ny/kings/brooklyn.html

```bash
perl -pe 's/   .*//' | uniq | perl -ne 'print unless /^([WE] )?\d/' | perl -ne 'print if /.../'
```

