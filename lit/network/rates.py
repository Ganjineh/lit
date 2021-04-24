from collections import OrderedDict
from decimal import ROUND_DOWN
from functools import wraps
from time import time

import requests

from lit.utils import Decimal

DEFAULT_CACHE_TIME = 60

# Constant for use in deriving exchange
# rates when given in terms of 1 BTC.
ONE = Decimal(1)

# https://en.bitcoin.it/wiki/Units
SATOSHI = 1
uLTC = 10 ** 2
mLTC = 10 ** 5
LTC = 10 ** 8

SUPPORTED_CURRENCIES = OrderedDict([
    ('satoshi', 'Satoshi'),
    ('ubtc', 'MicroLitecoin'),
    ('mbtc', 'MilliLitecoin'),
    ('ltc', 'Litecoin'),
])

# https://en.wikipedia.org/wiki/ISO_4217
CURRENCY_PRECISION = {
    'satoshi': 0,
    'ultc': 2,
    'mltc': 5,
    'ltc': 8
}


def satoshi_to_satoshi():
    return SATOSHI


def ultc_to_satoshi():
    return uLTC


def mltc_to_satoshi():
    return mLTC


def ltc_to_satoshi():
    return LTC


EXCHANGE_RATES = {
    'satoshi': satoshi_to_satoshi,
    'ultc': ultc_to_satoshi,
    'mltc': mltc_to_satoshi,
    'ltc': ltc_to_satoshi
}


def currency_to_satoshi(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    satoshis = EXCHANGE_RATES[currency]()
    return int(satoshis * Decimal(amount))


def currency_to_ltc(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    val = EXCHANGE_RATES['ltc']()
    return float(Decimal(amount)/val)


class CachedRate:
    __slots__ = ('satoshis', 'last_update')

    def __init__(self, satoshis, last_update):
        self.satoshis = satoshis
        self.last_update = last_update


def currency_to_satoshi_local_cache(f):
    start_time = time()

    cached_rates = dict([
        (currency, CachedRate(None, start_time)) for currency in EXCHANGE_RATES.keys()
    ])

    @wraps(f)
    def wrapper(amount, currency):
        now = time()

        cached_rate = cached_rates[currency]

        if not cached_rate.satoshis or now - cached_rate.last_update > DEFAULT_CACHE_TIME:
            cached_rate.satoshis = EXCHANGE_RATES[currency]()
            cached_rate.last_update = now

        return int(cached_rate.satoshis * Decimal(amount))

    return wrapper


@currency_to_satoshi_local_cache
def currency_to_satoshi_local_cached(amount, currency):
    pass  # pragma: no cover


def currency_to_satoshi_cached(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`. Results are cached
    using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    return currency_to_satoshi_local_cached(amount, currency)


def satoshi_to_currency(num, currency):
    """Converts a given number of satoshi to another currency as a formatted
    string rounded down to the proper number of decimal places.

    :param num: The number of satoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    return '{:f}'.format(
        Decimal(
            num / Decimal(EXCHANGE_RATES[currency]())
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )


def satoshi_to_currency_cached(num, currency):
    """Converts a given number of satoshi to another currency as a formatted
    string rounded down to the proper number of decimal places. Results are
    cached using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param num: The number of satoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    print(Decimal('0.' + '0' * CURRENCY_PRECISION[currency]))
    return '{:f}'.format(
        Decimal(num / Decimal(EXCHANGE_RATES[currency]()))
        .quantize(Decimal('0.' + '0' * CURRENCY_PRECISION[currency]), rounding=ROUND_DOWN)
        .normalize()
    )
