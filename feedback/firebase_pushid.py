"""Generate unique firebase push ids.

Lightly modified from https://gist.github.com/risent/4cab3878d995bec7d1c2
The only difference is the addition of a time_secs parameter to next_id().
"""

import random
import time
from exceptions import ValueError


class PushID(object):
    # Modeled after base64 web-safe chars, but ordered by ASCII.
    PUSH_CHARS = ('-0123456789'
                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                  '_abcdefghijklmnopqrstuvwxyz')

    def __init__(self):

        # Timestamp of last push, used to prevent local collisions if you
        # pushtwice in one ms.
        self.lastPushTime = 0

        # We generate 72-bits of randomness which get turned into 12
        # characters and appended to the timestamp to prevent
        # collisions with other clients.  We store the last characters
        # we generated because in the event of a collision, we'll use
        # those same characters except "incremented" by one.
        self.lastRandChars = [0] * 12

    def next_id(self, time_msecs):
        now = int(time_msecs)
        duplicateTime = (now == self.lastPushTime)
        self.lastPushTime = now
        timeStampChars = [''] * 8

        for i in range(7, -1, -1):
            timeStampChars[i] = self.PUSH_CHARS[now % 64]
            now = int(now / 64)

        if (now != 0):
            raise ValueError('We should have converted the entire timestamp.')

        uid = ''.join(timeStampChars)

        if not duplicateTime:
            for i in range(12):
                self.lastRandChars[i] = int(random.random() * 64)
        else:
            # If the timestamp hasn't changed since last push, use the
            # same random number, except incremented by 1.
            for i in range(11, -1, -1):
                if self.lastRandChars[i] == 63:
                    self.lastRandChars[i] = 0
                else:
                    break
            self.lastRandChars[i] += 1

        for i in range(12):
            uid += self.PUSH_CHARS[self.lastRandChars[i]]

        if len(uid) != 20:
            raise ValueError('Length should be 20.')
        return uid
