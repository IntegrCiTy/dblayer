from dblayer import *
from dblayer.func.func_citydb_view import *


def add_generic_attributes( access, cityobject_id, attr ):
    '''
    Helper function fr adding generic attributes to a city object.

    :param access: instance of database interface (DBAccess)
    :param cityobject_id: ID of the city object (int)
    :param attr: dictionary of generic attributes (dict of int/float/str)
    '''
    if not isinstance( access, DBAccess ):
        raise TypeError( 'parameter \'access\' must be of type \'DBAccess\'' )

    for name, value in attr.items():
        if isinstance( value, int ):
            access.add_citydb_object(
                insert_genericattrib_integer,
                attrname = name,
                attrvalue = value,
                cityobject_id = cityobject_id
            )
        elif isinstance( value, float ):
            access.add_citydb_object(
                insert_genericattrib_real,
                attrname = name,
                attrvalue = value,
                cityobject_id = cityobject_id
            )
        elif isinstance( value, str ):
            access.add_citydb_object(
                insert_genericattrib_string,
                attrname = name,
                attrvalue = value,
                cityobject_id = cityobject_id
            )
        else:
            raise TypeError( 'type not supported: {}'.format( value.__class__.__name__) )
