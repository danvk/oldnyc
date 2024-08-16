# User-generated feedback

OldNYC incorporates user feedback in a variety of ways, most notably:

  * Detection of rotated images
  * OCR correction

This document describes how to pull in new user feedback and push the
changes to the site.

This assumes that the `oldnyc` and `oldnyc.github.io` repos are
side-by-side on the file system.

## Step 1: Pull down data from Firebase

Usage:

    curl "https://brilliant-heat-1088.firebaseio.com/.json?print=pretty" -o feedback/user-feedback.json
    cp feedback/user-feedback.json feedback/user-feedback.$(date +%Y-%m-%dT%H:%M:%S).json

This will update `feedback/user-feedback.json`.

## Step 2: Update rotations

Run:

    cd analysis/rotations
    ./extract_rotations.py

This will update `analysis/rotations/corrections.json`

Commit all the rotations and you'll be able to review them via `git webdiff` when you run `generate_rotated_images.py` in the oldnyc.github.io repo.

If there are bad rotations, add them to `BLACKLIST` in `extract_rotations.py`.

To review the changes before committing, use this [localturk] template:

```bash
(echo 'photo_id,rotation'; git diff rotations.json | grep '^\+' | grep -v 'last_date' | sed 1d | sed 's/\+ *"//' | sed 's/,//' | sed 's/": /,/') > /tmp/new-rotations.txt
localturk template.html /tmp/new-rotations.txt checked-rotations.txt
```

[localturk]: https://github.com/danvk/localturk

## Step 3: Update OCR

Run:

    cd ocr/feedback
    ./extract_user_ocr.py
    ./ocr_corrector.py

This will update `ocr/feedback/{corrections,fixes}.json`.
`corrections.json` is an exhaustive list of new OCR corrections, while
`fixes.json` includes just one corrected version of the text for each
image.

To manually review updates, open review/index.html in a browser.

To reject some changes, re-run `ocr_corrector.py` as it suggests.

## Step 4: Update the static site

Run:

    ./generate_static_site.py
    cd ../oldnyc.github.io
    git diff

Look over the changes to make sure they seem reasonable. Then update the
rotated image assets (if needed):

    ./generate_rotated_images.py

Look over the rotated images. If any are incorrect, add them to the blacklist
in `extract_rotations.py` and rerun that step (and `generate_static_site.py`).

Finally, commit and push. You may need to purge the CloudFlare cache to
see the changes.
