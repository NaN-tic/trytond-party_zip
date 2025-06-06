
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool


class PartyZipTestCase(ModuleTestCase):
    'Test PartyZip module'
    module = 'party_zip'

    @with_transaction()
    def test_address(self):
        'Create address'
        pool = Pool()
        Party = pool.get('party.party')
        Address = pool.get('party.address')
        Country = pool.get('country.country')
        Subdivision = pool.get('country.subdivision')
        PostalCode = pool.get('country.postal_code')

        # allowed subdivisions by country code
        # ('ES', ('autonomous city', 'province'))
        # ('ID', ('autonomous province', 'province', 'special district', 'special region'))
        # ('IT', ('province',))
        country1, country2 = Country.create([{
                    'name': 'Country 1',
                    'code': 'ES',
                    }, {
                    'name': 'Country 2',
                    'code': 'IT',
                    }])
        subdivision1, subdivision2, subdivision3 = Subdivision.create([{
                    'code': '1',
                    'name': 'Subdivision 1',
                    'type': 'province',
                    'country': country1.id,
                    }, {
                    'code': '2',
                    'name': 'Subdivision 2',
                    'type': 'province',
                    'country': country2.id,
                    }, {
                    'code': '3',
                    'name': 'Subdivision 3',
                    'type': 'area',
                    'country': country2.id,
                    }])
        postal_code1, postal_code2, postal_code3 = PostalCode.create([{
                    'postal_code': 'postal_code1',
                    'city': 'city1',
                    'country': country1.id,
                    'subdivision': subdivision1.id,
                    }, {
                    'postal_code': 'postal_code2',
                    'city': 'city2',
                    'country': country2.id,
                    'subdivision': subdivision2.id,
                    }, {
                    'postal_code': 'postal_code3',
                    'city': 'city3',
                    'country': country2.id,
                    'subdivision': subdivision3.id,
                    }])
        party1, = Party.create([{
                    'name': 'Party 1',
                    }])
        address, = Address.create([{
                    'party': party1.id,
                    'street': 'St sample, 15',
                    'city': 'City',
                    }])
        self.assertEqual(address.postal_code, None)
        self.assertEqual(address.city, 'City')
        Address.write([address], {
                    'location': postal_code1.id,
                    })
        self.assertEqual(address.postal_code, 'postal_code1')
        self.assertEqual(address.city, 'city1')
        self.assertEqual(address.country.id, country1.id)
        self.assertEqual(address.subdivision.id, subdivision1.id)

        Address.write([address], {
                    'location': postal_code2.id,
                    })
        self.assertEqual(address.postal_code, 'postal_code2')
        self.assertEqual(address.city, 'city2')
        self.assertEqual(address.country.id, country2.id)
        self.assertEqual(address.subdivision.id, subdivision2.id)

        PostalCode.write([postal_code2], {
                    'postal_code': 'Postal Code 3',
                    'city': 'CITY 3',
                    'country': country1.id,
                    'subdivision': subdivision1.id,
                    })
        address, = Address.browse([address.id])
        self.assertEqual(address.postal_code, 'Postal Code 3')
        self.assertEqual(address.city, 'CITY 3')
        self.assertEqual(address.country.id, country1.id)
        self.assertEqual(address.subdivision.id, subdivision1.id)

        # not allow subdivision
        Address.write([address], {
                    'country': country2.id,
                    'location': postal_code3.id,
                    })
        self.assertEqual(address.postal_code, 'postal_code3')
        self.assertEqual(address.city, 'city3')
        self.assertEqual(address.country.id, country2.id)
        self.assertEqual(address.subdivision, None)

del ModuleTestCase
