from .db_orm import *

from collections import namedtuple

import warnings

from sqlalchemy import create_engine, and_
from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy import exc as sa_exc
from sqlalchemy.sql import select
from sqlalchemy.orm import Session, sessionmaker, mapper

import psycopg2


PostgreSQLConnectionInfo = namedtuple( 'PostgreSQLConnectionInfo', [ 'user', 'pwd', 'host', 'port', 'dbname' ] )


class DBAccess:
    """
    Base class for accessing the database.
    """

    # Static flag to check whether ORM mapping has already been done.
    orm_mapping_done = False

    def __init__( self ):
        pass

    def connect_to_db( self, connection_info ):
        """
        Connect to the database by initializing an engine and a session.

        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        :return: database engine and session (sqlalchemy.engine.Engine, sqlalchemy.orm.session.Session)
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
        engine = create_engine( db_connection_string )

        # Create session.
        session = sessionmaker( bind = engine )

        return engine, session


    def init_orm( self, engine ):
        """
        Initialize the object relational mapping of the database.
        """
        # Check if mapping has already been done.
        if DBAccess.orm_mapping_done is True:
            return

        # Retrieve meta data.
        metadata = MetaData( engine )
        #metadata.reflect()

        with warnings.catch_warnings():
            warnings.simplefilter( "ignore", category = sa_exc.SAWarning )

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
        DBAccess.orm_mapping_done = True


    def cleanup_schema( self, connection_info ):
        """
        Clean-up the database, i.e., delete the content of all tables and views.

        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        :return: none
        """
        if not isinstance( connection_info, PostgreSQLConnectionInfo ):
            raise TypeError( 'parameter \'connection_info\' must be of type \'PostgreSQLConnectionInfo\'' )

        # Make low-level connection (via psycopg2).
        connection = psycopg2.connect(
            user = connection_info.user,
            password = connection_info.pwd,
            host = connection_info.host,
            port = connection_info.port,
            dbname = connection_info.dbname )

        # Get cursor and execute 'cleanup_schema' function.
        connection.cursor().execute( 'SELECT sim_pkg.cleanup_schema();' )

        # Commit the changes.
        connection.commit()
