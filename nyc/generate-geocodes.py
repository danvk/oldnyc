#!/usr/bin/python
#
# This script runs all the locations in the records pickle through the
# google maps geocoder.
#
# Run it from the 'sfhistory' directory, via:
# ./nyc/generate-geocodes.py --maps_key ... nyc/records.pickle


import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 

import cPickle
import record
import csv

