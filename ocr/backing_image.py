#!/usr/bin/env python

import re

import record


class NothingOnBackError(Exception):
    pass


def getBackOfPhotoUrl(record_or_photo_id):
    '''record is a record.Record object or a photo id.

    Either returns the URL of the back-of-the-card image, or raises
    NothingOnBackError.
    '''

    if isinstance(record_or_photo_id, record.Record):
        return getBackOfPhotoUrl(record_or_photo_id.photo_id())

    photo_id = record_or_photo_id
    assert isinstance(photo_id, basestring)

    if not re.match(r'[0-9]+f', photo_id):
        raise NothingOnBackError()

    return 'http://images.nypl.org/?id=%s&t=w' % photo_id.replace('f', 'b')


if __name__ == '__main__':
    rs = record.AllRecords('nyc/records.pickle')
    for r in rs:
        try:
            print '\t'.join(['ocr/images/%s.jpg' % r.photo_id(), getBackOfPhotoUrl(r)])
        except NothingOnBackError:
            pass
