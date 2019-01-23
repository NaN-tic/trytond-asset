# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import configuration
from . import asset
from . import party


def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationSequence,
        asset.Asset,
        asset.AssetAddress,
        module='asset', type_='model')
    Pool.register(
        party.PartyReplace,
        module='asset', type_='wizard')
