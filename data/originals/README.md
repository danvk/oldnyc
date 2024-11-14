# Data Sources

Files in this folder are "originals"—not derived from some other data source.

- `data/originals/Milstein_data_for_DV.csv`: CSV from the NYPL (2024)
- Street listings
  - `manhattan-streets.txt`: https://geographic.org/streetview/usa/ny/new_york/new_york.html
  - `brooklyn-streets.txt`: https://geographic.org/streetview/usa/ny/kings/brooklyn.html

```bash
perl -pe 's/   .*//' | uniq | perl -ne 'print unless /^([WE] )?\d/' | perl -ne 'print if /.../'
```

Files related to the 2024 change from Ocropus → GPT-based OCR:

- `ocr-heavy-editor.ids.txt`: backing IDs of items that were reviewed by heavy users of the OldNYC OCR Corrector (heavy = 100+ edits).
- `ocr-big-movers.txt`: Dan's manual review of ~500 items with a large edit distance between the existing on-site OCR and GPT.
- `ocr-spelld25.txt`: Dan's manual review of ~80 items where GPT has more misspelled words and the length of the transcriptions varied by 25+ characters.
- `ocr-followup.txt`: More manual choices from follow-up review.
