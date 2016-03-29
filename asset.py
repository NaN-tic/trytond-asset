# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.pyson import Eval, If
from trytond.transaction import Transaction
from trytond import backend

__all__ = ['Asset']


class Asset(ModelSQL, ModelView):
    'Asset'
    __name__ = 'asset'
    company = fields.Many2One('company.company', 'Company', required=True,
        select=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ])
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
        t = cls.__table__()
        cls._sql_constraints = [
            ('code_uniq', Unique(t, t.code),
                'The code of the asset must be unique.')
            ]

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        pool = Pool()
        Company = pool.get('company.company')
        cursor = Transaction().cursor
        table = TableHandler(cursor, cls, module_name)
        sql_table = cls.__table__()
        company_table = Company.__table__()
        created_company = not table.column_exist('company')

        super(Asset, cls).__register__(module_name)

        # Migration: new company field
        if created_company:
            # Don't use UPDATE FROM because SQLite nor MySQL support it.
            value = company_table.select(company_table.id, limit=1)
            cursor.execute(*sql_table.update([sql_table.company], [value]))

    def get_rec_name(self, name):
        name = '[%s]' % self.code
        if self.name:
            name += ' %s' % self.name
        return name

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('code',) + tuple(clause[1:]),
            ('name',) + tuple(clause[1:]),
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

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    def get_code_readonly(self, name):
        return True

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
