# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond import backend
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pool import Pool
from trytond.pyson import Eval, Id
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)

__all__ = ['Configuration', 'ConfigurationSequence']


class Configuration(
        ModelSingleton, ModelSQL, ModelView, CompanyMultiValueMixin):
    'Asset Configuration'
    __name__ = 'asset.configuration'
    asset_sequence = fields.MultiValue(fields.Many2One(
            'ir.sequence', "Asset Sequence",
            domain=[
                ('company', 'in',
                    [Eval('context', {}).get('company', -1), None]),
                ('sequence_type', '=', Id('asset', 'sequence_type_asset')),
                ]))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'asset_sequence':
            return pool.get('asset.configuration.sequence')
        return super(Configuration, cls).multivalue_model(field)

    @classmethod
    def default_asset_sequence(cls, **pattern):
        return cls.multivalue_model('asset_sequence').default_asset_sequence()


class ConfigurationSequence(ModelSQL, CompanyValueMixin):
    "Asset Configuration Sequence"
    __name__ = 'asset.configuration.sequence'
    asset_sequence = fields.Many2One(
        'ir.sequence', "Asset Sequence",
        domain=[
            ('company', 'in', [Eval('company', -1), None]),
            ('sequence_type', '=', Id('asset', 'sequence_type_asset')),
            ])

    @classmethod
    def default_asset_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('asset', 'sequence_asset')
        except KeyError:
            return None
