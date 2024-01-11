# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, If, Bool


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'
    location = fields.Many2One('country.postal_code', 'Location',
        ondelete='RESTRICT', domain=[
            If(Bool(Eval('country')), ('country', '=', Eval('country', -1)),
                ()),
            If(Bool(Eval('subdivision')),
                ('subdivision', '=', Eval('subdivision', -1)), ()),
            ])

    @classmethod
    def __setup__(cls):
        super(Address, cls).__setup__()
        cls.postal_code.readonly = True
        cls.city.readonly = True
        eval_location = Bool(Eval('location'))
        if cls.country.states.get('readonly'):
            cls.country.states['readonly'] |= eval_location
        else:
            cls.country.states['readonly'] = eval_location
        if cls.subdivision.states.get('readonly'):
            cls.subdivision.states['readonly'] = eval_location
        else:
            cls.subdivision.states['readonly'] = eval_location

    @classmethod
    def __register__(cls, module):
        # Migration from 5.8: rename country_zip to location
        table_h = cls.__table_handler__(module)
        table_h.column_rename('country_zip', 'location')
        super().__register__(module)

    @staticmethod
    def update_location_values(values):
        pool = Pool()
        PostalCode = pool.get('country.postal_code')

        values = values.copy()
        if 'location' in values:
            if values['location']:
                postal_codes = PostalCode.search([
                        ('id', '=', values['location']),
                        ], limit=1)
                # In some rare cases it can happen that country_zip ID does not
                # exist in the database. In that case we avoid crashing and, we
                # set country_zip, zip and city to NULL
                if postal_codes:
                    postal_code, = postal_codes
                    values['postal_code'] = postal_code.postal_code
                    values['city'] = postal_code.city
                    values['country'] = postal_code.country.id
                    values['subdivision'] = (postal_code.subdivision.id if
                        postal_code.subdivision else None)
                    return values
                else:
                    values['location'] = None

            values['postal_code'] = None
            values['city'] = None
        return values

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        new_vlist = []
        for values in vlist:
            new_vlist.append(cls.update_location_values(values))
        return super(Address, cls).create(new_vlist)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        new_args = []
        for addresses, values in zip(actions, actions):
            new_args.append(addresses)
            new_args.append(cls.update_location_values(values))
        super(Address, cls).write(*new_args)

    @fields.depends('location')
    def on_change_location(self):
        if self.location:
            self.postal_code = self.location.postal_code
            self.city = self.location.city
            self.country = self.location.country
            self.subdivision = self.location.subdivision
        else:
            self.postal_code = None
            self.city = None


class PostalCode(metaclass=PoolMeta):
    __name__ = 'country.postal_code'

    def get_rec_name(self, name):
        res = []
        if self.postal_code:
            res.append(self.postal_code)
        if self.city:
            res.append(self.city)
        res = [' '.join(res)]
        if self.subdivision:
            res.append(self.subdivision.rec_name)
        res = [' - '.join(res)]
        res.append('(%s)' % self.country.rec_name)
        return ' '.join(res)

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            [('postal_code',) + tuple(clause[1:])],
            [('city',) + tuple(clause[1:])],
            ]

    @classmethod
    def write(cls, *args):
        Address = Pool().get('party.address')

        super().write(*args)

        actions = iter(args)
        fields = set(['postal_code', 'city', 'country', 'subdivision'])
        to_update = []
        for locations, values in zip(actions, actions):
            intersec = set(values.keys()) & fields
            if not intersec:
                continue
            addresses = Address.search([
                    ('location', 'in', [x.id for x in locations]),
                    ])
            to_update.append(addresses)
            address_values = {}
            for field in intersec:
                address_values[field] = values[field]
            to_update.append(address_values)

        Address.write(*to_update)
