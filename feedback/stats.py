#!/usr/bin/env python
"""Generate stats on the Firebase JSON dump."""

import json
from collections import Counter
from datetime import datetime

# Ignore feedback from before this date.
start_date = "2017-06-01"

skipped = 0
count = 0

types = set(
    [
        "rotate",
        "large-border",
        "text",
        "wrong-location",
        "multiples",
        "notext",
        "rotate-backing",
        "date",
        "cut-in-half",
    ]
)
type_counts = Counter()
date_counts = Counter()
month_counts = Counter()

feedback = json.load(open("feedback/user-feedback.json"))["feedback"]

for photo_id, feedbacks in feedback.items():
    for feedback_type, feedback_entries in feedbacks.items():
        for feedback in feedback_entries.values():
            metadata = feedback["metadata"]
            timestamp = metadata["timestamp"]
            date = datetime.fromtimestamp(timestamp / 1000)
            dt = date.strftime("%Y-%m-%d")

            if dt < start_date:
                skipped += 1
                continue
            count += 1

            type_counts[feedback_type] += 1
            date_counts[dt] += 1
            month_counts[dt[:7]] += 1

print("Skipped %d records" % skipped)
print("Included %d records" % count)
print("Type counts:\n%s\n" % json.dumps(type_counts, indent=2, sort_keys=True))

print("By date:\n%s\n" % json.dumps(date_counts, indent=2, sort_keys=True))
print("By month:\n%s\n" % json.dumps(month_counts, indent=2, sort_keys=True))
