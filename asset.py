# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.pyson import Eval, If
from trytond.transaction import Transaction
from trytond import backend
from trytond.pyson import Date


__all__ = ['Asset', 'AssetAddress']


class AssetAssigmentMixin(ModelSQL, ModelView):

    from_date = fields.Date('From Date', required=True)
    through_date = fields.Date('Through Date')

    @classmethod
    def validate(cls, assigments):
        super(AssetAssigmentMixin, cls).validate(assigments)
        for assigment in assigments:
            assigment.check_dates()

    @classmethod
    def __setup__(cls):
        super(AssetAssigmentMixin, cls).__setup__()
        cls._order.insert(0, ('from_date', 'DESC'))
        cls._error_messages.update({
            'dates_overlaps': ('"%(first)s" and "%(second)s" assigment'
                'overlap.'),
            })

    def check_dates(self):
        cursor = Transaction().cursor
        table = self.__table__()
        cursor.execute(*table.select(table.id,
                where=(((table.from_date <= self.from_date)
                        & (table.through_date >= self.from_date))
                    | ((table.from_date <= self.through_date)
                        & (table.through_date >= self.through_date))
                    | ((table.from_date >= self.from_date)
                        & (table.through_date <= self.through_date)))
                & (table.asset == self.asset.id)
                & (table.id != self.id)))
        assigment = cursor.fetchone()
        if assigment:
            overlapping_period = self.__class__(assigment[0])
            self.raise_user_error('dates_overlaps', {
                    'first': self.rec_name,
                    'second': overlapping_period.rec_name,
                    })


class AssetAddress(AssetAssigmentMixin):
    'Asset Address'

    __name__ = 'asset.address'

    address = fields.Many2One('party.address', 'Address', required=True)
    contact = fields.Many2One('party.party', 'Contact')
    asset = fields.Many2One('asset', 'Asset', required=True)


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
    address = fields.One2Many('asset.address', 'asset', 'Address')
    current_address = fields.Function(fields.Many2One('party.address',
        'Current Address'), 'get_current_address')
    current_contact = fields.Function(fields.Many2One('party.party',
        'Current Contact'), 'get_current_address')

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

    @classmethod
    def get_current_values(cls, assets, Class):
        Date_ = Pool().get('ir.date')
        today = Date_.today()
        cursor = Transaction().cursor
        table = Class.__table__()
        cursor.execute(*table.select(
                table.id,
                table.asset,
                where=(((table.from_date <= today)
                        & (table.through_date >= today))
                & (table.asset.in_([x.id for x in assets]))
                )))

        res = dict((r[1], r[0]) for r in cursor.fetchall())
        return res

    @classmethod
    def get_current_address(cls, assets, names):
        pool = Pool()
        AssetAddress = pool.get('asset.address')
        assigments = cls.get_current_values(assets, AssetAddress)
        result = {}
        for name in names:
            result[name] = dict((i.id, None) for i in assets)

        for asset, assigment_id in assigments.iteritems():
            if not assigment_id:
                continue
            assigment = AssetAddress(assigment_id)
            result['current_address'][asset] = assigment.address.id
            result['current_contact'][asset] = assigment.contact and \
                assigment.contact.id
        return result

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
