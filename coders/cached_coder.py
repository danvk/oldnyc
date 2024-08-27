#!/usr/bin/python
#
# Instead of coding records, this coder loads results from a cache written out by a previous run. This can be used to speed up iteration.

import cPickle

class CachedCoder:
  def __init__(self, name):
    self._name = name
    unpickler = cPickle.Unpickler(open('/tmp/coder.%s.pickle' % name, 'r'))
    recs = unpickler.load()
    self._recs = {}

    for photo_id, loc in recs:
      self._recs[photo_id] = loc

  def codeRecord(self, r):
    if r['id'] not in self._recs: return None
    return self._recs[r['id']]

  def name(self):
    return self._name
