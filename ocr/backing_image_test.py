from nose.tools import *

import record
from ocr import backing_image


def makeRecord(photo_id):
    r = record.Record()
    r.tabular = {'i': [photo_id]}
    return r


def test_makeRecord():
    eq_('12345', makeRecord('12345').photo_id())


def test_getBackOfPhotoUrl():
    eq_('http://images.nypl.org/?id=720946b&t=w',
        backing_image.getBackOfPhotoUrl('720946f'))

    eq_('http://images.nypl.org/?id=720946b&t=w',
        backing_image.getBackOfPhotoUrl(makeRecord('720946f')))

    with assert_raises(backing_image.NothingOnBackError):
        backing_image.getBackOfPhotoUrl('2903480')
