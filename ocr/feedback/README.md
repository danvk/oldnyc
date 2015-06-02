To update OCR corrections, update user-feedback.csv and run:

    ./extract_user_ocr.py
    ./ocr_corrector.py

I might need to do some de-duping of photo ids. Users could correct the text
from two different photos on the same card.

I included a cookie! Hooray!
  --> but does it work correctly?
      (e.g. photo with five identical IPs but different cookies)
      It seems to not work; basically every cookie is unique.

When there are multiple disagreeing interpretations, I could pick the one
that comes from the cookie with the most fixes. Or pick the one with the
most changes. Or pick one randomly.

After stepping through 100 photos with corrections, I saw absolutely no
spam. Simply accepting corrections is going to work fine.

Which one to accept?
  first de-dupe by IP
  if there's agreement between any two, use that.
  otherwise, pick the one with the largest diff.

Next time I do an update, make sure that 700391f-a has a complete
description.
