from . import scenario as _scenario
from .db_orm import *
from .db_func import *

from collections import namedtuple

from sqlalchemy import create_engine #, MetaData, Table, Column, Integer
from sqlalchemy.sql import select #, func
from sqlalchemy.orm import Session, sessionmaker #, mapper

import psycopg2


PostgreSQLConnectionInfo = namedtuple( 'PostgreSQLConnectionInfo', [ 'user', 'pwd', 'host', 'port', 'dbname' ] )


def write_to_db( connection_info, scenario ):
    """
    Write scenario to database. Requires SimulationPackage schema to be installed.
    """
    if not isinstance( scenario, _scenario.Scenario ):
        raise TypeError( 'parameter \'scenario\' must be of type \'Scenario\'' )

    # Connect to database.
    engine, session = connect_to_db( connection_info )

    # Start session.
    s = session()
    
    # Define function call to insert simulation to database.
    insert_sim = func_insert_simulation( scenario )

    # Store simulation and retrieve the ID of its database representation. 
    sim_query = s.query( insert_sim ).one()
    sim_id = sim_query[0]

    port_ids = {}
    
    # Iterate through the scenario's nodes.
    for node_name, node in scenario.nodes.items():
        # Define function call to insert node to database.
        insert_node = func_insert_node( sim_id, node )

        # Store node and retrieve the ID of its database representation. 
        result = s.query( insert_node ).one()
        node_id = result[0]

        input_port_ids = {}
        output_port_ids = {}

        for input_port_name in node.input_ports.keys():
            # Define function call to insert input port to database.
            insert_port = func_insert_port( node_id, 'input', input_port_name )

            # Store port and retrieve the ID of its database representation. 
            result = s.query( insert_port ).one()
            input_port_id = result[0]

            # Save the ID (may be needed when saving links).
            input_port_ids[input_port_name] = input_port_id

        for output_port_name in node.output_ports.keys():
            # Define function call to insert output port to database.
            insert_port = func_insert_port( node_id, 'output', output_port_name )

            # Store port and retrieve the ID of its database representation. 
            result = s.query( insert_port ).one()
            output_port_id = result[0]

            # Save the ID (may be needed when saving links).
            output_port_ids[output_port_name] = output_port_id

        # Collect data about all input/outputs port IDs for this node.
        port_ids[ node_name ] = {
            'inputs' : input_port_ids,
            'outputs' : output_port_ids
            }

    # Iterate through the scenario's links.
    for link_name, link in scenario.links.items():
        # Retrieve information about the link's input port: node name, variable name, port id 
        from_node_name = link.output_port.node.node_name
        from_node_var = link.output_port.variable_name
        from_port_id = port_ids[from_node_name]['outputs'][from_node_var]

        # Retrieve information about the link's input port: node name, variable name, port id 
        to_node_name = link.input_port.node.node_name
        to_node_var = link.input_port.variable_name
        to_port_id = port_ids[to_node_name]['inputs'][to_node_var]

        # Define function call to insert link to database.
        insert_link = func_insert_port_connection( sim_id, link_name, from_port_id, to_port_id )

        # Store link and retrieve the ID of its database representation. 
        result = s.query( insert_link ).one()
        link_id = result[0]

    # Commit session.
    s.commit()

    # Close session.
    session.close_all()
    

def read_from_db( connection_info, simulation_name ):
    """
    Read scenario from database. Requires SimulationPackage schema to be installed. Returns a new schema.
    """
    # Connect to database.
    engine, session = connect_to_db( connection_info )

    # Initialize object relational mapper.
    init_orm( engine )

    # Create scenario.
    scenario = _scenario.Scenario( simulation_name )

    try:
        # Retrieve the simulation ID.
        sim_query = session().query( Simulation ).filter_by( name = simulation_name ).one()
        sim_id = sim_query.id

        # Retrieve information about nodes, ports and links belonging to the simulation ID.
        links = session().query( PortConnectionExt ).filter_by( simulation_id = sim_id ).all()
        nodes = session().query( Node ).filter_by( simulation_id = sim_id ).all()

        # Add nodes.
        for n in nodes:
            scenario.create_and_add_node( n.name )

        # Add links.
        for l in links:
            from_node_name = l.n1_name if l.p1_type == 'output' else l.n2_name
            output_variable_name = l.p1_variable_name if l.p1_type == 'output' else l.p2_variable_name
            to_node_name = l.n1_name if l.p1_type == 'input' else l.n2_name
            input_variable_name = l.p1_variable_name if l.p1_type == 'input' else l.p2_variable_name    

            scenario.get_node( from_node_name ).add_output_port( output_variable_name )
            scenario.get_node( to_node_name ).add_input_port( input_variable_name )
            scenario.create_and_add_link( l.name, from_node_name, output_variable_name, to_node_name, input_variable_name )

    except Exception as e:
        cleanup_orm()
        raise e
        
    # Clean-up this session.
    session.close_all()
    cleanup_orm()

    # Return the scenario.
    return scenario


def connect_to_db( connection_info ):
    """
    Connect to the database. Returns a tuple containing the corresponding engine and session.
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


def cleanup_schema( connection_info ):
    """
    Clean-up the database, i.e., delete the content of all tables and views.
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
