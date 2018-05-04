# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
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
        Zip = pool.get('country.zip')

        country1, country2 = Country.create([{
                    'name': 'Country 1',
                    }, {
                    'name': 'Country 2',
                    }])
        subdivision1, subdivision2 = Subdivision.create([{
                    'code': '1',
                    'name': 'Subdivision 1',
                    'type': 'area',
                    'country': country1.id,
                    }, {
                    'code': '2',
                    'name': 'Subdivision 2',
                    'type': 'area',
                    'country': country2.id,
                    }])
        zip1, zip2 = Zip.create([{
                    'zip': 'zip1',
                    'city': 'city1',
                    'country': country1.id,
                    'subdivision': subdivision1.id,
                    }, {
                    'zip': 'zip2',
                    'city': 'city2',
                    'country': country2.id,
                    'subdivision': subdivision2.id,
                    }])
        party1, = Party.create([{
                    'name': 'Party 1',
                    }])
        address, = Address.create([{
                    'party': party1.id,
                    'street': 'St sample, 15',
                    'city': 'City',
                    }])
        self.assertEqual(address.zip, None)
        self.assertEqual(address.city, 'City')
        Address.write([address], {
                    'country_zip': zip1.id,
                    })
        self.assertEqual(address.zip, 'zip1')
        self.assertEqual(address.city, 'city1')
        self.assertEqual(address.country.id, country1.id)
        self.assertEqual(address.subdivision.id, subdivision1.id)

        Address.write([address], {
                    'country_zip': zip2.id,
                    })
        self.assertEqual(address.zip, 'zip2')
        self.assertEqual(address.city, 'city2')
        self.assertEqual(address.country.id, country2.id)
        self.assertEqual(address.subdivision.id, subdivision2.id)

        Zip.write([zip2], {
                    'zip': 'ZIP 3',
                    'city': 'CITY 3',
                    'country': country1.id,
                    'subdivision': subdivision1.id,
                    })
        address, = Address.browse([address.id])
        self.assertEqual(address.zip, 'ZIP 3')
        self.assertEqual(address.city, 'CITY 3')
        self.assertEqual(address.country.id, country1.id)
        self.assertEqual(address.subdivision.id, subdivision1.id)


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        PartyZipTestCase))
    return suite
