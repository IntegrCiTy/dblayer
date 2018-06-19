from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import array

def insert_genericattrib_integer(
    attrname,
    attrvalue,
    cityobject_id,
    id = None,
    parent_genattrib_id = None,
    root_genattrib_id = None
    ):
    """
    Define function call to insert generic attribute (integer value).
    """
    return func.citydb_view.insert_cityobject_genericattrib_integer(
        attrname, # character varying
        attrvalue, # integer
        cityobject_id, # integer
        id, # integer, default:: NULL::integer
        parent_genattrib_id, # integer,, default:: NULL::integer
        root_genattrib_id # integer, default:: NULL::integer
        )


def insert_genericattrib_real(
    attrname,
    attrvalue,
    cityobject_id,
    id = None,
    parent_genattrib_id = None,
    root_genattrib_id = None
    ):
    """
    Define function call to insert generic attribute (integer value).
    """
    return func.citydb_view.insert_cityobject_genericattrib_real(
        attrname, # character varying
        attrvalue, # double precision
        cityobject_id, # integer
        id, # integer, default:: NULL::integer
        parent_genattrib_id, # integer,, default:: NULL::integer
        root_genattrib_id # integer, default:: NULL::integer
        )


def insert_genericattrib_string(
    attrname,
    attrvalue,
    cityobject_id,
    id = None,
    parent_genattrib_id = None,
    root_genattrib_id = None
    ):
    """
    Define function call to insert generic attribute (integer value).
    """
    return func.citydb_view.insert_cityobject_genericattrib_string(
        attrname, # character varying
        attrvalue, # character varying
        cityobject_id, # integer
        id, # integer, default:: NULL::integer
        parent_genattrib_id, # integer,, default:: NULL::integer
        root_genattrib_id # integer, default:: NULL::integer
        )
