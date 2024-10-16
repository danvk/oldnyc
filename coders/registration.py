#!/usr/bin/python

from typing import Callable

from coders.types import Coder

coders: list[Callable[[], Coder]] = []


def registerCoderClass(klass):
    global coders
    coders.append(klass)


def coderClasses():
    global coders
    return coders
