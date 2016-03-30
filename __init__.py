# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .configuration import *
from .asset import *


def register():
    Pool.register(
        Configuration,
        Asset,
        AssetAddress,
        module='asset', type_='model')
