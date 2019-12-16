from .orm.orm_simpkg import *

from collections import namedtuple

import warnings

from sqlalchemy import create_engine, and_
from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy import exc as sa_exc
from sqlalchemy.sql import select
from sqlalchemy.orm import Session, sessionmaker, mapper
from sqlalchemy.sql.functions import Function as SQLFunction

import psycopg2

# Tuple containing information requried to connect to the database.
PostgreSQLConnectionInfo = namedtuple( 'PostgreSQLConnectionInfo', [ 'user', 'pwd', 'host', 'port', 'dbname' ] )

# Tuple containing information about the existing object representation in the database.
ObjectClassInfo = namedtuple( 'ObjectClassInfo', [ 'id', 'schema', 'table_name' ] )

# Tuple containing information about the mapped object representation.
MappedClassInfo = namedtuple( 'MappedClassInfo', [ 'impl', 'schema', 'table_name' ] )


class DBAccess:
    """
    Base class for accessing the database.
    """

    # Flag to check whether ORM mapping for the Simulation Package has already been done.
    simpkg_orm_mapping_init = False

    # Flag to check whether ORM mapping for the CityDB has already been initialized.
    citydb_orm_mapping_init = False

    # List of all classes in 3dCityDB (to be retrieved from CityDB).
    citydb_objectclass_list = {}

    # List of mapped classes from 3DCityDB.
    citydb_objectclass_map = {}


    def __init__( self ):
        self.engine = None
        self.session = None
        self.current_session = None
        self.connection_info = None


    def connect_to_citydb( self, connection_info ):
        """
        Connect to the database by initializing an engine and a session.

        :return: none
        """
        if not isinstance( connection_info, PostgreSQLConnectionInfo ):
            raise TypeError( 'parameter \'connection_info\' must be of type \'PostgreSQLConnectionInfo\'' )

        # Construct connection string.
        db_connection_string = str()

        if isinstance( connection_info, PostgreSQLConnectionInfo ):
            db_connection_string = 'postgresql://{0}:{1}@{2}:{3}/{4}'
            db_connection_string = db_connection_string.format(
                connection_info.user,
                connection_info.pwd,
                connection_info.host,
                connection_info.port,
                connection_info.dbname
                )
        else:
            err_msg = 'unrecognized type for parameter \'connection_info\''
            raise RuntimeError( err_msg )

        # Connect to database.
        self.engine = create_engine( db_connection_string )

        # Create session.
        self.session = sessionmaker( bind = self.engine )

        # Save database connection information.
        self.connection_info = connection_info


    def start_citydb_session( self ):
        """
        Start a new database session.

        :return: none
        """
        if self.engine is None or self.session is None:
            raise RuntimeError( 'not connected to database' )

        # Start a new session.
        self.current_session = self.session()


    def commit_citydb_session( self ):
        """
        Commit changes of the current session to the database.

        :return: none
        """
        if self.current_session is not None: self.current_session.commit()


    def add_citydb_object( self, func, **args ):
        """
        Add a new object to the database.

        :param func: inserter function (sqlalchemy.sql.functions.Function)
        :return: returns the scalar return value of the inserter function (typically an object-specific ID)
        """
        # Check if parameter 'func' is a callable object (function)
        if not callable( func ):
            raise TypeError( 'parameter \'func\' must be a function returning type \'sqlalchemy.sql.functions.Function\'' )

        # Start new session if necessary.
        if self.current_session is None: self.start_citydb_session()

        # Retrieve inserter function.
        inserter_func = func( **args )

        # Check if 'inserter_func' is a function of type 'sqlalchemy.sql.functions.Function'
        if not isinstance( inserter_func, SQLFunction ):
            raise TypeError( 'parameter \'func\' must be a function returning type \'sqlalchemy.sql.functions.Function\'' )

        return self.current_session.query( inserter_func ).one()[0]


    def get_citydb_objects( self, class_name, table_name = None, schema = None, conditions = None ):
        """
        Retrieve all objects of one type from the database.

        :param class_name: name of mapped object class (string)
        :param table: alternative table name (string, optional)
        :param schema: alternative schema name (string, optional)
        :param conditions: list of filters applied when retrieving the objects (list of sqlalchemy.sql.elements.BinaryExpression, optional)

        :return: list of results
        """
        # Retrieve mapped class representing the object.
        ObjectClass = self.map_citydb_object_class( class_name, table_name, schema )

        # Start a new database session if necessary.
        if self.current_session is None: self.start_citydb_session()

        # Retrieve class info.
        class_info = DBAccess.citydb_objectclass_list[ class_name ]

        if conditions is None: conditions = []

        if not class_info.id is None:
            try:
                # In case the mapped class has an attribute called 'objectclass_id', set it
                # to the according value retrieved from table 'citydb.objectclass'. This is
                # required when retrieving objects from tables that store more than one type
                # of object (with the different types distinguished using 'objectclass_id').
                conditions.append( ObjectClass.objectclass_id == class_info.id )
            except AttributeError:
                # The object does not have an attribute called 'objectclass_id' (because the
                # according table does not have it). No need to worry, just ignore it ...
                pass

        filter_conditions = and_( *conditions )

        return self.current_session.query( ObjectClass ).filter( filter_conditions ).all()


    def join_citydb_objects( self, class_names, conditions, result_index = None ):
        """
        Retrieve selected objects from the database by 'joining' more than one table or view. The tables or views are represented by object classes, which have to mapped before performing this operation.

        :param class_names: list name of mapped object class (list of string)
        :param conditions: list of filters applied when retrieving the objects (list of sqlalchemy.sql.elements.BinaryExpression, optional)
        :param result_index: restrict results to the collection output associated to this index, i.e., if result_index == N then only the results for the (N+1)th object class will be returned (int, optional)

        :return: list of results, with each entry a collection of associated result objects (list of sqlalchemy.util._collections.result), unless parameter result_index is specified (see above)
        """
        # Retrieve mapped classes representing the objects.
        object_classes = []
        for class_name in class_names:
            ObjectClass = self.map_citydb_object_class( class_name )

            # Retrieve class info.
            class_info = DBAccess.citydb_objectclass_list[ class_name ]

            if not class_info.id is None:
                try:
                    # In case the mapped class has an attribute called 'objectclass_id', set it
                    # to the according value retrieved from table 'citydb.objectclass'. This is
                    # required when retrieving objects from tables that store more than one type
                    # of object (with the different types distinguished using 'objectclass_id').
                    conditions.append( ObjectClass.objectclass_id == class_info.id )
                except AttributeError:
                    # The object does not have an attribute called 'objectclass_id' (because the
                    # according table does not have it). No need to worry, just ignore it ...
                    pass

            object_classes.append( ObjectClass )

        # Start a new database session if necessary.
        if self.current_session is None: self.start_citydb_session()

        filter_conditions = and_( *conditions )

        query_result = self.current_session.query( *object_classes ).filter( filter_conditions ).all()

        return \
            [ result for result in query_result ] if result_index is None else \
            [ result[result_index] for result in query_result ]


    def execute_function( self, func ):
        """
        Execute SQL function.

        :param func: SQL function (sqlalchemy.sql.functions.Function)
        :return: returns the scalar return value of the SQL function (typically an object-specific ID)
        """
        # Check if 'inserter_func' is a function of type 'sqlalchemy.sql.functions.Function'
        if not isinstance( func, SQLFunction ):
            raise TypeError( 'parameter \'func\' must be a function returning type \'sqlalchemy.sql.functions.Function\'' )

        # Start new session if necessary.
        if self.current_session is None: self.start_citydb_session()

        return self.current_session.query( func ).one()[0]


    def cleanup_simpkg_schema( self ):
        """
        Clean-up the simulation package database, i.e., delete the content of all tables and views related to the simulation package.

        :return: none
        """
        if self.connection_info is None:
            raise RuntimeError( 'not connected to database' )

        # Make low-level connection (via psycopg2).
        connection = psycopg2.connect(
            user = self.connection_info.user,
            password = self.connection_info.pwd,
            host = self.connection_info.host,
            port = self.connection_info.port,
            dbname = self.connection_info.dbname )

        # Get cursor and execute 'cleanup_schema' function.
        connection.cursor().execute( 'SELECT sim_pkg.cleanup_schema();' )

        # Commit the changes.
        connection.commit()


    def cleanup_citydb_schema( self ):
        """
        Clean-up the 3DCityDB database, i.e., delete the content of all tables and views related to the 3DCityDB.

        :return: none
        """
        if self.connection_info is None:
            raise RuntimeError( 'not connected to database' )

        # Make low-level connection (via psycopg2).
        connection = psycopg2.connect(
            user = self.connection_info.user,
            password = self.connection_info.pwd,
            host = self.connection_info.host,
            port = self.connection_info.port,
            dbname = self.connection_info.dbname )

        # Get cursor and execute 'cleanup_schema' function.
        connection.cursor().execute( 'SELECT citydb_pkg.cleanup_schema();' )

        # Commit the changes.
        connection.commit()


    def map_citydb_object_class( self, class_name, table_name = None, schema = None, user_defined = True ):
        # Check if ORM for 3DCityDB has already been initialized.
        if DBAccess.citydb_orm_mapping_init is False:
            self._init_citydb_orm()

        if class_name not in DBAccess.citydb_objectclass_list and user_defined is True:
            if table_name is None:
                raise RuntimeError( 'a table name must be specified for user-defined mappings' )
            if schema is None:
                raise RuntimeError( 'a schema must be specified for user-defined mappings' )

            # Add user-defined mapping to list.
            DBAccess.citydb_objectclass_list[ class_name ] = \
                ObjectClassInfo( id = None, schema = schema, table_name = table_name )

        try:
            # Retrieve class info.
            objectclass_info = DBAccess.citydb_objectclass_list[ class_name ]

            # Check if class has already been mapped.
            try:
                mapped_class_info = DBAccess.citydb_objectclass_map[ class_name ]

                schema_changed = ( schema is not None ) and ( mapped_class_info.schema is not schema )
                table_name_changed = ( table_name is not None ) and ( mapped_class_info.table_name is not table_name )

                if schema_changed or table_name_changed:
                    # The class has already been mapped from the specified schema/table.
                    if schema is None: schema = mapped_class_info.schema
                    if table_name is None: table_name = mapped_class_info.table_name

                    # Issue a warning, then re-map the class
                    err = 'Class {} has already been mapped from table: {} (schema: {}). '
                    err += 'It will be re-mapped from table: {} (schema: {}).'
                    err = err.format( class_name, mapped_class_info.table_name,
                        mapped_class_info.schema, table_name, schema )
                    warnings.warn( err, RuntimeWarning )
                else:
                    # The class has already been mapped from the specified schema/table.
                    return mapped_class_info.impl
            except KeyError:
                # The class has not been mapped before --> just continue.
                # Use default values in case no schema or table has been given explicitly.
                if schema is None: schema = objectclass_info.schema
                if table_name is None: table_name = objectclass_info.table_name

            # Define dummy class (but with correct name) for mapping.
            MappedClass = type( class_name, (), {} )

            # Retrieve meta data.
            metadata = MetaData( self.engine )

            with warnings.catch_warnings():
                warnings.simplefilter( 'ignore', category = sa_exc.SAWarning )

                table_mappedclass = None

                # Define table to be mapped.
                if schema is 'citydb_view':
                    table_mappedclass = Table( table_name, metadata,
                        Column( 'id', Integer, primary_key = True ),
                        autoload = True, schema = schema )
                else:
                    table_mappedclass = Table( table_name, metadata,
                        autoload = True, schema = schema )

                # Map the class to the table.
                mapper( MappedClass, table_mappedclass )

            # Store mapped class.
            DBAccess.citydb_objectclass_map[ class_name ] = \
                MappedClassInfo( impl = MappedClass, schema = schema, table_name = table_name )

            return MappedClass

        except KeyError:
            # The object class name is not known --> raise error.
            raise RuntimeError( 'unknown object class: {}'.format( class_name ) )


    def _init_citydb_orm( self ):
        """
        Initialize the object relational mapping of the Simulation Package.
        """
        if self.engine is None or self.session is None:
            raise RuntimeError( 'not connected to database' )

        # Check if mapping has already been initialized.
        if DBAccess.citydb_orm_mapping_init is True:
            return

        # Retrieve meta data.
        metadata = MetaData( self.engine )

        # Define class for holding information about object classes defined in database.
        ObjectClass = type( 'ObjectClass', (), {} )

        with warnings.catch_warnings():
            warnings.simplefilter( 'ignore', category = sa_exc.SAWarning )

            # Describe table 'citydb.objectclass'.
            table_objectclass = Table( 'objectclass', metadata, autoload = True, schema = 'citydb' )

            # Map table to class ObjectClass.
            mapper( ObjectClass, table_objectclass )

        # Retrieve object classes from database.
        if self.current_session is None: self.start_citydb_session()
        objectclass = self.current_session.query( ObjectClass ).all()

        # Store overview of object classes as defined in schema 'citydb' (default representation).
        for oc in objectclass:
            DBAccess.citydb_objectclass_list[ oc.classname ] = \
                ObjectClassInfo( id = oc.id, table_name = oc.tablename, schema = 'citydb' )

        # Generic attributes are not listed --> add manually.
        DBAccess.citydb_objectclass_list[ 'GenericAttribute' ] = \
            ObjectClassInfo( id = None, table_name = 'cityobject_genericattrib', schema = 'citydb' )

        # Add also specialized representations of generic attributes (from 'citydb_view').
        DBAccess.citydb_objectclass_list[ 'GenericAttributeReal' ] = \
            ObjectClassInfo( id = None, table_name = 'cityobject_genericattrib_real', schema = 'citydb_view' )
        DBAccess.citydb_objectclass_list[ 'GenericAttributeInteger' ] = \
            ObjectClassInfo( id = None, table_name = 'cityobject_genericattrib_int', schema = 'citydb_view' )
        DBAccess.citydb_objectclass_list[ 'GenericAttributeString' ] = \
            ObjectClassInfo( id = None, table_name = 'cityobject_genericattrib_string', schema = 'citydb_view' )

        # Set flag to indicate that mapping has been initialized.
        DBAccess.citydb_orm_mapping_init = True


    def _init_simpkg_orm( self ):
        """
        Initialize the object relational mapping of the Simulation Package.
        """
        if self.engine is None or self.session is None:
            raise RuntimeError( 'not connected to database' )

        # Check if mapping has already been done.
        if DBAccess.simpkg_orm_mapping_init is True:
            return

        # Retrieve meta data.
        metadata = MetaData( self.engine )
        #metadata.reflect()

        with warnings.catch_warnings():
            warnings.simplefilter( 'ignore', category = sa_exc.SAWarning )

            # Describe table 'sim_pkg.simulation'.
            table_simulation = Table(
                'simulation',
                metadata,
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe table 'sim_pkg.tool'.
            table_simulation_tool = Table(
                'tool',
                metadata,
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe table 'sim_pkg.node'.
            table_node = Table(
                'node',
                metadata,
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe table 'sim_pkg.port'.
            table_port = Table(
                'port',
                metadata,
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe view 'sim_pkg.port_connection_ext'.
            view_port_connection_ext = Table(
                'port_connection_ext',
                metadata,
                Column( 'id', Integer, primary_key = True ),
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe view 'sim_pkg.generic_parameter_tool'.
            view_generic_parameter_tool = Table(
                'generic_parameter_tool',
                metadata,
                Column( 'id', Integer, primary_key = True ),
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe view 'sim_pkg.generic_parameter_node'.
            view_generic_parameter_node = Table(
                'generic_parameter_node',
                metadata,
                Column( 'id', Integer, primary_key = True ),
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe view 'sim_pkg.generic_parameter_sim'.
            view_generic_parameter_sim = Table(
                'generic_parameter_sim',
                metadata,
                Column( 'id', Integer, primary_key = True ),
                autoload = True,
                schema = 'sim_pkg'
                )

            # Describe table 'sim_pkg.port'.
            table_generic_attribute = Table(
                'cityobject_genericattrib',
                metadata,
                autoload = True,
                schema = 'citydb'
                )

        # Map tables and views to classes.
        mapper( Simulation, table_simulation )
        mapper( SimulationTool, table_simulation_tool )
        mapper( Node, table_node )
        mapper( Port, table_port )
        mapper( PortConnectionExt, view_port_connection_ext )
        mapper( GenericParameterTool, view_generic_parameter_tool )
        mapper( GenericParameterNode, view_generic_parameter_node )
        mapper( GenericParameterSimulation, view_generic_parameter_sim )
        mapper( GenericAttribute, table_generic_attribute )

        # Set flag to indicate that mapping has been done.
        DBAccess.simpkg_orm_mapping_init = True
