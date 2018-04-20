from .simpkg_orm import *

from collections import namedtuple

import warnings

from sqlalchemy import create_engine, and_
from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy import exc as sa_exc
from sqlalchemy.sql import select
from sqlalchemy.orm import Session, sessionmaker, mapper
from sqlalchemy.sql.functions import Function as SQLFunction

import psycopg2


PostgreSQLConnectionInfo = namedtuple( 'PostgreSQLConnectionInfo', [ 'user', 'pwd', 'host', 'port', 'dbname' ] )


MappedClassInfo = namedtuple( 'MappedClassInfo', [ 'impl', 'schema', 'tablename' ] )


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


    def get_citydb_objects( self, classname, tablename = None, schema = None, conditions = None ):
        # Retrieve mapped class representing the object.
        ObjectClass = self.map_citydb_object_class( classname, tablename, schema )

        # Start a new database session if necessary.
        if self.current_session is None: self.start_citydb_session()

        # Retrieve class info.
        class_info = DBAccess.citydb_objectclass_list[ classname ]

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


    def map_citydb_object_class( self, classname, tablename = None, schema = None ):
        # Check if ORM for 3DCityDB has already been initialized.
        if DBAccess.citydb_orm_mapping_init is False:
            self._init_citydb_orm()

        try:
            # Retrieve class info.
            objectclass_info = DBAccess.citydb_objectclass_list[ classname ]

            # Check if class has already been mapped.
            try:
                mapped_class_info = DBAccess.citydb_objectclass_map[ classname ]

                schema_changed = ( schema is not None ) and ( mapped_class_info.schema is not schema )
                tablename_changed = ( tablename is not None ) and ( mapped_class_info.tablename is not tablename )

                if schema_changed or tablename_changed:
                    # The class has already been mapped from the specified schema/table.
                    if schema is None: schema = mapped_class_info.schema
                    if tablename is None: tablename = mapped_class_info.tablename

                    # Issue a warning, then re-map the class
                    err = 'Class {} will has already been mapped from table: {} (schema: {}). '
                    err += 'It will be re-mapped from table: {} (schema: {}).'
                    err = err.format( classname, mapped_class_info.tablename,
                        mapped_class_info.schema, tablename, schema )
                    warnings.warn( err, RuntimeWarning )
                else:
                    # The class has already been mapped from the specified schema/table.
                    return mapped_class_info.impl
            except KeyError:
                # The class has not been mapped before --> just continue.
                # Use default values in case no schema or table has been given explicitly.
                if schema is None: schema = 'citydb'
                if tablename is None: tablename = objectclass_info.tablename

            # Define dummy class (but with correct name) for mapping.
            MappedClass = type( classname, (), {} )

            # Retrieve meta data.
            metadata = MetaData( self.engine )

            with warnings.catch_warnings():
                warnings.simplefilter( 'ignore', category = sa_exc.SAWarning )

                table_mappedclass = None

                # Define table to be mapped.
                if schema is 'citydb_view':
                    table_mappedclass = Table( tablename, metadata,
                        Column( 'id', Integer, primary_key = True ),
                        autoload = True, schema = schema )
                else:
                    table_mappedclass = Table( tablename, metadata,
                        autoload = True, schema = schema )

                # Map the class to the table.
                mapper( MappedClass, table_mappedclass )

            # Store mapped class.
            DBAccess.citydb_objectclass_map[ classname ] = \
                MappedClassInfo( impl = MappedClass, schema = schema, tablename = tablename )

            return MappedClass

        except KeyError:
            # The object class name is not known --> raise error.
            raise RuntimeError( 'unknown object class: {}'.format( classname ) )


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

        # Store object classes in dedicated list.
        for oc in objectclass:
            DBAccess.citydb_objectclass_list[ oc.classname ] = oc

        # Generic attributes are not listed --> add manually.
        genericattric = ObjectClass()
        genericattric.classname = 'GenericAttribute'
        genericattric.tablename = 'cityobject_genericattrib'
        DBAccess.citydb_objectclass_list[ genericattric.classname ] = genericattric

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

        # Map tables and views to classes.
        mapper( Simulation, table_simulation )
        mapper( SimulationTool, table_simulation_tool )
        mapper( Node, table_node )
        mapper( Port, table_port )
        mapper( PortConnectionExt, view_port_connection_ext )
        mapper( GenericParameterTool, view_generic_parameter_tool )
        mapper( GenericParameterNode, view_generic_parameter_node )
        mapper( GenericParameterSimulation, view_generic_parameter_sim )

        # Set flag to indicate that mapping has been done.
        DBAccess.simpkg_orm_mapping_init = True
