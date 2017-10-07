# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import configuration
from . import asset


def register():
    Pool.register(
        configuration.Configuration,
        asset.Asset,
        asset.AssetAddress,
        module='asset', type_='model')
