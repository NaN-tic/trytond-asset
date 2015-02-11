#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Asset']


class Asset(ModelSQL, ModelView):
    'Asset'
    __name__ = 'asset'
    name = fields.Char('Name')
    code = fields.Char('Code', required=True, select=True,
        states={
            'readonly': Eval('code_readonly', True),
            },
        depends=['code_readonly'])
    code_readonly = fields.Function(fields.Boolean('Code Readonly'),
        'get_code_readonly')
    product = fields.Many2One('product.product', 'Product',
        domain=[
            ('type', 'in', ['assets', 'goods']),
            ])
    type = fields.Selection([
            ('', ''),
            ], 'Type', select=True)
    active = fields.Boolean('Active')

    @classmethod
    def __setup__(cls):
        super(Asset, cls).__setup__()
        cls._sql_constraints = [
            ('code_uniq', 'UNIQUE(code)',
                'The code of the asset must be unique.')
            ]

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_code_readonly():
        Configuration = Pool().get('asset.configuration')
        config = Configuration(1)
        return bool(config.asset_sequence)

    @staticmethod
    def default_type():
        return Transaction().context.get('type', '')

    def get_code_readonly(self, name):
        return True

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('code',) + tuple(clause[1:]),
            ('name',) + tuple(clause[1:]),
            ]

    @classmethod
    def create(cls, vlist):
        Sequence = Pool().get('ir.sequence')
        Configuration = Pool().get('asset.configuration')

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('code'):
                config = Configuration(1)
                values['code'] = Sequence.get_id(config.asset_sequence.id)
        return super(Asset, cls).create(vlist)

    @classmethod
    def copy(cls, assets, default=None):
        if default is None:
            default = {}
        default.setdefault('code', None)
        return super(Asset, cls).copy(assets, default=default)
