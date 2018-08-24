# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, If, Bool

__all__ = ['Address', 'CountryZip']


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'
    country_zip = fields.Many2One('country.zip', 'Location',
        ondelete='RESTRICT', domain=[
            If(Bool(Eval('country')), ('country', '=', Eval('country', -1)),
                ()),
            If(Bool(Eval('subdivision')),
                ('subdivision', '=', Eval('subdivision', -1)), ()),
            ], depends=['country', 'subdivision'])

    @classmethod
    def __setup__(cls):
        super(Address, cls).__setup__()
        cls.zip.readonly = True
        cls.city.readonly = True
        cls.country.states['readonly'] |= Bool(Eval('country_zip'))
        cls.subdivision.states['readonly'] |= Bool(Eval('country_zip'))

    @staticmethod
    def update_zip_values(CountryZip, values):
        values = values.copy()
        if 'country_zip' in values:
            if values['country_zip']:
                country_zip, = CountryZip.search([
                        ('id', '=', values['country_zip']),
                        ], limit=1)
                values['zip'] = country_zip.zip
                values['city'] = country_zip.city
                values['country'] = country_zip.country.id
                values['subdivision'] = (country_zip.subdivision.id if
                    country_zip.subdivision else None)
            else:
                values['zip'] = None
                values['city'] = None
        return values

    @classmethod
    def create(cls, vlist):
        CountryZip = Pool().get('country.zip')
        new_vlist = []
        for values in vlist:
            new_vlist.append(cls.update_zip_values(CountryZip, values))
        return super(Address, cls).create(new_vlist)

    @classmethod
    def write(cls, *args):
        CountryZip = Pool().get('country.zip')
        actions = iter(args)
        new_args = []
        for addresses, values in zip(actions, actions):
            new_args.append(addresses)
            new_args.append(cls.update_zip_values(CountryZip, values))
        super(Address, cls).write(*new_args)

    @fields.depends('country_zip')
    def on_change_country_zip(self):
        if self.country_zip:
            self.zip = self.country_zip.zip
            self.city = self.country_zip.city
            self.country = self.country_zip.country
            self.subdivision = self.country_zip.subdivision
        else:
            self.zip = None
            self.city = None


class CountryZip(metaclass=PoolMeta):
    __name__ = 'country.zip'

    def get_rec_name(self, name):
        res = []
        if self.zip:
            res.append(self.zip)
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
            [('zip',) + tuple(clause[1:])],
            [('city',) + tuple(clause[1:])],
            ]

    @classmethod
    def write(cls, *args):
        Address = Pool().get('party.address')

        super(CountryZip, cls).write(*args)

        actions = iter(args)
        fields = set(['zip', 'city', 'country', 'subdivision'])
        to_update = []
        for zips, values in zip(actions, actions):
            intersec = set(values.keys()) & fields
            if not intersec:
                continue
            addresses = Address.search([
                    ('country_zip', 'in', [x.id for x in zips]),
                    ])
            to_update.append(addresses)
            address_values = {}
            for field in intersec:
                address_values[field] = values[field]
            to_update.append(address_values)

        Address.write(*to_update)
