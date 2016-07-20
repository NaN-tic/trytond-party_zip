# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .party import *

def register():
    Pool.register(
        Address,
        CountryZip,
        module='party_zip', type_='model')
