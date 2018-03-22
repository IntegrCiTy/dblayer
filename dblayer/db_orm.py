import warnings

from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import mapper, clear_mappers


class Simulation( object ):
    """
    Define class for retrieving data from table 'sim_pkg.simulation'.
    """
    def __init__( self, name ):
        self.name = name


class SimulationTool( object ):
    """
    Define class for retrieving data from table 'sim_pkg.tool'.
    """
    def __init__( self, name ):
        self.name = name


class Node( object ):
    """
    Define class for retrieving data from table 'sim_pkg.node'.
    """
    def __init__( self, name ):
        self.name = name


class PortConnectionExt( object ):
    """
    Define class for retrieving data from view 'sim_pkg.port_connection_ext'.
    """
    def __init__( self, name ):
        self.name = name


class GenericParameterTool( object ):
    """
    Define class for retrieving data from view 'sim_pkg.generic_parameter_tool'.
    """
    def __init__( self, name ):
        self.name = name


def init_orm( engine ):
    """
    Initialize the object relational mapping of the database.
    """
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

    # Map tables and views to classes.
    mapper( Simulation, table_simulation )
    mapper( SimulationTool, table_simulation_tool )
    mapper( Node, table_node )
    mapper( PortConnectionExt, view_port_connection_ext )
    mapper( GenericParameterTool, view_generic_parameter_tool )


def cleanup_orm():
    """
    Undo object relational mapping of the database (remove current mappers from classes).
    """
    # Remove current mappers from classes.
    clear_mappers()
