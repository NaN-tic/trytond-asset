# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.asset.tests.test_asset import suite
except ImportError:
    from .test_asset import suite

__all__ = ['suite']
