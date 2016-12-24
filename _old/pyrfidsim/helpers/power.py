import numpy as np


def dbm2mw(value):
    return 10**(value/10)


def mw2dbm(value):
    return 10 * np.log10(value)


def db2ratio(value):
    return 10**(value/10)


def ratio2db(value):
    return 10 * np.log10(value)
