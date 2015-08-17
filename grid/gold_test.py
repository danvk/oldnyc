from nose.tools import *

from grid import gold

def test_make_street_str():
    eq_('1st street', gold.make_street_str(1))
    eq_('2nd street', gold.make_street_str(2))
    eq_('3rd street', gold.make_street_str(3))
    eq_('4th street', gold.make_street_str(4))
    eq_('9th street', gold.make_street_str(9))
    eq_('11th street', gold.make_street_str(11))
    eq_('12th street', gold.make_street_str(12))
    eq_('13th street', gold.make_street_str(13))
    eq_('21st street', gold.make_street_str(21))
    eq_('22nd street', gold.make_street_str(22))
    eq_('100th street', gold.make_street_str(100))
    eq_('101st street', gold.make_street_str(101))
    eq_('102nd street', gold.make_street_str(102))
    eq_('121st street', gold.make_street_str(121))


def test_make_avenue_str():
    eq_('Avenue A', gold.make_avenue_str(0))
    eq_('Avenue D', gold.make_avenue_str(-3))
    eq_('1st Avenue', gold.make_avenue_str(1))
    eq_('2nd Avenue', gold.make_avenue_str(2))
    eq_('3rd Avenue', gold.make_avenue_str(3))

    eq_('Park Avenue South', gold.make_avenue_str(4, 17))
    eq_('Park Avenue South', gold.make_avenue_str(4, 32))
    eq_('Park Avenue', gold.make_avenue_str(4, 59))
