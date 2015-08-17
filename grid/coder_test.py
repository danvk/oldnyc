from nose.tools import *

from grid import coder


def assert_close(ll1, ll2):
    '''Assert that two latitude & longitude tuples are "close".'''
    try:
        assert_almost_equal(ll1[0], ll2[0], places=6)
        assert_almost_equal(ll1[1], ll2[1], places=6)
    except AssertionError as e:
        print '%s != %s' % (ll1, ll2)
        raise e


def test_exact():
    # It's really Park Avenue South.
    assert_close(coder.code('4', '17'), (40.736518, -73.988962))

def test_interpolate():
    # This is halfway between 26th & 28th.
    assert_close(coder.code('9', '27'), (40.749020, -73.9995210))

def test_extrapolate():
    assert_close(coder.code('A', '15'), (40.731083, -73.979847))
    assert_close(coder.code('A', '20'), (40.734071, -73.977654))

def test_may_extrapolate():
    assert(coder.may_extrapolate('A', '15'))
    assert(coder.may_extrapolate('2', '8'))
    assert(coder.may_extrapolate('A', '25'))
    assert(not coder.may_extrapolate('4', '8'))
    assert(not coder.may_extrapolate('D', '25'))
    assert(not coder.may_extrapolate('7', '10'))
    assert(not coder.may_extrapolate('B', '93'))  # 723557f-c
