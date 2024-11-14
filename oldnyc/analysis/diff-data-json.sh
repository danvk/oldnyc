#!/bin/bash
# This is handy for getting a pretty diff of images.njdson,
# so long as the diff isn't too big.

set -o errexit

git diff data/images.ndjson | grep '^-{' | sed 's/^-//' | jq . > /tmp/before.ndjson
git diff data/images.ndjson | grep '^\+{' | sed 's/^\+//' | jq . > /tmp/after.ndjson
webdiff /tmp/before.ndjson /tmp/after.ndjson
