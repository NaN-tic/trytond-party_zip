# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, ModelView
from trytond.pool import PoolMeta

__all__ = ['Address']
__metaclass__ = PoolMeta


# TODO: Create a view that adds 'country_zip' field and hides the following
# fields in the form view:
#
# - zip
# - city
# - country
# - subdivision
#
# (I think it is better to hide rather than replace so that other inheriting
# modules will still be compatible)
#
# For tree view I think it is better to keep existing fields


class Address:
    __name__ = 'party.address'
    country_zip = fields.Many2One('country.zip', 'Location')

# TODO: Given that I think there are some issues if we try to redefine those
# fields as Function ones, we could consider storing their value in the
# database on write. The problem we need to consider is what happens if a field
# from country.zip is changed. Should we 'simply' propagate the new values to
# existing addresses?

