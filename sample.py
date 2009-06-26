import glob
import random
import record

def LoadSample(file_pattern, num):
  """Load a subset of the records matching file_pattern."""
  ret = []
  seen= 0
  for filename in glob.glob(file_pattern):
    seen += 1
    if len(ret) < num:
      r = record.Record.FromString(file(filename).read())
      if r: ret.append(r)
    else:
      n = random.randint(0, seen - 1)
      if n < num:
        r = record.Record.FromString(file(filename).read())
        if r: ret[n] = r
  return ret
