# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond import backend
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.tools.multivalue import migrate_property
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
                ('code', '=', 'asset'),
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
            ('code', '=', 'asset'),
            ],
        depends=['company'])

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        exist = TableHandler.table_exist(cls._table)

        super(ConfigurationSequence, cls).__register__(module_name)

        if not exist:
            cls._migrate_property([], [], [])

    @classmethod
    def _migrate_property(cls, field_names, value_names, fields):
        field_names.append('asset_sequence')
        value_names.append('asset_sequence')
        fields.append('company')
        migrate_property(
            'asset.configuration', field_names, cls, value_names,
            fields=fields)

    @classmethod
    def default_asset_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('asset', 'sequence_asset')
        except KeyError:
            return None
