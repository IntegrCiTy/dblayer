from sqlalchemy.sql import func


def insert_surface_geometry(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    parent_id = None,
    root_id = None,
    is_solid = None,
    is_composite = None,
    is_triangulated = None,
    is_xlink = None,
    is_reverse = None,
    solid_geometry = None,
    geometry = None,
    implicit_geometry = None,
    cityobject_id = None
    ):
    """
    Define function call to insert surface geometry into the database.
    """
    return func.citydb_pkg.insert_surface_geometry(
        id, # integer, default: NULL::integer
        gmlid, # character varying, default: NULL::character varying
        gmlid_codespace, # character varying, default: NULL::character varying
        parent_id, # integer, default: NULL::integer
        root_id, # integer, default: NULL::integer
        is_solid, # numeric, default: NULL::numeric
        is_composite, # numeric, default: NULL::numeric
        is_triangulated, # numeric, default: NULL::numeric
        is_xlink, # numeric, default: NULL::numeric
        is_reverse, # numeric, default: NULL::numeric
        solid_geometry, # geometry, default: NULL::geometry
        geometry, # geometry, default: NULL::geometry
        implicit_geometry, # geometry, default: NULL::geometry
        cityobject_id # integer, default: NULL::integer
        )