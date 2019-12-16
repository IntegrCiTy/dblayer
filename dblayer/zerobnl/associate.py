from sqlalchemy.inspection import inspect


class AssociateCityDBObjectAttribute:
    """Link to database table entry associated to the attribute of a 3DCityDB object."""

    def __init__( self, obj, attr_name ):
        if not isinstance( attr_name, str ):
            raise TypeError( 'parameter \'attr_name\' must be of type \'str\'' )

        if not hasattr( obj, attr_name ):
            raise RuntimeError( 'object has no attribute called \'attr_name\'' )

        obj_inspect = inspect( obj )
        primary_key = obj_inspect.identity[0]

        class_inspect = inspect( type( obj ) )
        mapped_table = class_inspect.persist_selectable

        self.table_name = '.'.join( [ mapped_table.schema , mapped_table.name ] )
        self.object_id = primary_key
        self.column_name = attr_name


class AssociateCityDBGenericAttribute:
    """Link to database table entry associated to a 3DCityDB generic attribute."""

    def __init__( self, attr ):
        self.attribute_name = attr.attrname
        self.attribute_id = attr.id
