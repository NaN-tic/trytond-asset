======================
Party Replace Scenario
======================

Imports::

    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company

Install asset::

    >>> config = activate_modules('asset')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create a party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Customer')
    >>> party.save()
    >>> party2 = Party(name='Customer')
    >>> party2.save()

Create asset::

    >>> Asset = Model.get('asset')
    >>> AssetAddress = Model.get('asset.address')
    >>> asset = Asset()
    >>> asset.name = 'Asset'
    >>> asset.save()
    >>> asset_adress = AssetAddress()
    >>> asset_adress.asset = asset
    >>> asset_adress.address = party.addresses[0]
    >>> asset_adress.contact = party
    >>> asset_adress.save()

Try replace active party::

    >>> replace = Wizard('party.replace', models=[party])
    >>> replace.form.source = party
    >>> replace.form.destination = party2
    >>> replace.execute('replace')

Check fields have been replaced::

    >>> asset_adress.reload()
    >>> asset_adress.contact == party2
    True
