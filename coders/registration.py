#!/usr/bin/python

coders = []
def registerCoderClass(klass):
  global coders
  coders.append(klass)

def coderClasses():
  global coders
  return coders
