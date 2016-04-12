# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields

__all__ = ['Configuration']


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'Asset Configuration'
    __name__ = 'asset.configuration'
    asset_sequence = fields.Property(fields.Many2One('ir.sequence',
            'Asset Sequence', domain=[
                ('code', '=', 'asset'),
                ]))
