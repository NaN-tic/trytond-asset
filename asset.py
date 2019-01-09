# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import date
from sql import Null

from trytond import backend
from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.pool import Pool
from trytond.pyson import Eval, If, Bool
from trytond.transaction import Transaction

__all__ = ['Asset', 'AssetAddress']


class AssetAssignmentMixin(ModelSQL, ModelView):
    from_date = fields.Date('From Date',
        domain=[If(Bool(Eval('through_date')),
                ('from_date', '<=', Eval('through_date')),
                ())],
        depends=['through_date'])
    through_date = fields.Date('Through Date',
        domain=[If(Bool(Eval('through_date')),
                ('through_date', '>=', Eval('from_date')),
                ())],
        depends=['from_date'])

    @classmethod
    def __setup__(cls):
        super(AssetAssignmentMixin, cls).__setup__()
        cls._order.insert(0, ('from_date', 'DESC'))

    @staticmethod
    def default_from_date():
        pool = Pool()
        Date = pool.get('ir.date')
        return Date.today()

    @classmethod
    def validate(cls, assignments):
        super(AssetAssignmentMixin, cls).validate(assignments)
        for assignment in assignments:
            assignment.check_dates()

    def check_dates(self):
        cursor = Transaction().connection.cursor()
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
        assignment = cursor.fetchone()
        if assignment:
            overlapping_period = self.__class__(assignment[0])
            raise UserError(gettext('asset.dates_overlaps',
                    first=self.rec_name,
                    second=overlapping_period.rec_name))


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
    addresses = fields.One2Many('asset.address', 'asset', 'Addresses')
    current_address = fields.Function(fields.Many2One('party.address',
            'Current Address'), 'get_current_address',
        searcher='search_current_address')
    current_contact = fields.Function(fields.Many2One('party.party',
            'Current Contact'), 'get_current_address',
        searcher='search_current_contact')

    @classmethod
    def __setup__(cls):
        super(Asset, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('code_uniq', Unique(t, t.code, t.company),
                'The code of the asset must be unique.')
            ]

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        Company = pool.get('company.company')
        TableHandler = backend.get('TableHandler')

        cursor = Transaction().connection.cursor()
        table = TableHandler(cls, module_name)
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
        cursor = Transaction().connection.cursor()
        table = Class.__table__()
        cursor.execute(*table.select(
                table.id,
                table.asset,
                where=(((table.from_date <= today) | (table.from_date == Null))
                    & ((table.through_date >= today)
                        | (table.through_date == Null))
                & (table.asset.in_([x.id for x in assets]))
                )))

        res = dict((r[1], r[0]) for r in cursor.fetchall())
        return res

    @classmethod
    def get_current_address(cls, assets, names):
        pool = Pool()
        AssetAddress = pool.get('asset.address')
        assignments = cls.get_current_values(assets, AssetAddress)
        result = {}
        for name in names:
            result[name] = dict((i.id, None) for i in assets)

        for asset, assignment_id in assignments.items():
            if not assignment_id:
                continue
            assignment = AssetAddress(assignment_id)
            if 'current_address' in result:
                result['current_address'][asset] = (assignment.address.id if
                    assignment.address else None)
            if 'current_contact' in result:
                result['current_contact'][asset] = (assignment.contact.id if
                    assignment.contact else None)
        return result

    @classmethod
    def search_current_address(cls, name, clause):
        if not clause[2]:
            return [('addresses',) + tuple(clause[1:])]
        return [('addresses.address',) + tuple(clause[1:])]

    @classmethod
    def search_current_contact(cls, name, clause):
        if not clause[2]:
            return [('addresses',) + tuple(clause[1:])]
        return [('addresses.contact',) + tuple(clause[1:])]

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


class AssetAddress(AssetAssignmentMixin):
    'Asset Address'
    __name__ = 'asset.address'
    asset = fields.Many2One('asset', 'Asset', required=True,
        ondelete='CASCADE')
    address = fields.Many2One('party.address', 'Address', required=True)
    contact = fields.Many2One('party.party', 'Contact')

    @classmethod
    def __register__(cls, module_name):
        super(AssetAddress, cls).__register__(module_name)
        pool = Pool()

        Asset = pool.get('asset')
        cursor = Transaction().connection.cursor()
        sql_table = cls.__table__()
        asset_table = Asset.__table__()

        TableHandler = backend.get('TableHandler')

        table = TableHandler(Asset, module_name)
        address_exist = table.column_exist('address')

        # Migration: address Many2One replaced by One2Many
        if address_exist:
            cursor.execute(*asset_table.select(asset_table.id,
                asset_table.address,
                where=asset_table.address != Null))
            for asset_id, address_id in cursor.fetchall():
                cursor.execute(*sql_table.insert([
                        sql_table.asset,
                        sql_table.address,
                        sql_table.from_date],
                    [[asset_id, address_id, date.min]]))
            table.drop_column('address')
