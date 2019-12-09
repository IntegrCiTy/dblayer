# def associate_to_citydb_object( value, table_name, object_id, column_name ):
    # DBAssociateObject = type(
        # 'DBAssociateObjectTo' + value.__class__.__name__.capitalize(),
        # ( type( value ), ),
        # { 'table_name' : table_name, 'object_id' : object_id, 'column_name' : column_name }
    # )
    # return DBAssociateObject( value )


# def associate_to_citydb_generic_attribute( value, attribute_name, attribute_id ):
    # DBAssociateGenericAttribute = type(
        # 'DBAssociateGenericAttributeTo' + value.__class__.__name__.capitalize(),
        # ( type( value ), ),
        # { 'attribute_name' : attribute_name, 'attribute_id' : attribute_id ]
    # )
    # return DBAssociateGenericAttribute( value )


class AssociateCityDBObject:
    """Link to database table entry associated to a 3DCityDB object via table name, object ID, and column name."""

    def __init__( self, table_name, object_id, column_name ):
        if not isinstance( table_name, str ):
            raise TypeError( 'parameter \'table_name\' must be of type \'str\'' )

        if not isinstance( object_id, int ):
            raise TypeError( 'parameter \'object_id\' must be of type \'int\'' )

        if not isinstance( column_name, str ):
            raise TypeError( 'parameter \'column_name\' must be of type \'str\'' )

        if not len( table_name.split( '.' ) ) == 2:
            raise RuntimeError( 'parameter \'table_name\' must be formated according to \'schema.table\'' )

        self.table_name = table_name
        self.object_id = object_id
        self.column_name = column_name


class AssociateCityDBGenericAttribute:
    """Link to database table entry associated to a 3DCityDB generic attribute via attribute name and ID."""

    def __init__( self, attribute_name, attribute_id ):
        if not isinstance( attribute_name, str ):
            raise TypeError( 'parameter \'attribute_name\' must be of type \'str\'' )

        if not isinstance( attribute_id, int ):
            raise TypeError( 'parameter \'attribute_id\' must be of type \'int\'' )

        self.attribute_name = attribute_name
        self.attribute_id = attribute_id
