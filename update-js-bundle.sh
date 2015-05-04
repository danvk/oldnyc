#!/bin/bash
cd viewer/static/js
cat $(cat files.txt) > bundle.js
