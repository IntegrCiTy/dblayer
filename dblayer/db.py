from . import scenario as _scenario
from .db_orm import *
from .db_func import *

from collections import namedtuple

from sqlalchemy import create_engine #, MetaData, Table, Column, Integer
from sqlalchemy.sql import select #, func
from sqlalchemy.orm import Session, sessionmaker #, mapper

import psycopg2


PostgreSQLConnectionInfo = namedtuple( 'PostgreSQLConnectionInfo', [ 'user', 'pwd', 'host', 'port', 'dbname' ] )


# Define separator for converting lists of string in comma-separated strings and vice versa.
__separator__ = ';'


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
        # Retrieve simulation tool from node.
        sim_tool = node.sim_tool

        # Write simulation tool information to database.
        tool_id = write_sim_tool_to_db( sim_tool, s )

        # Define function call to insert node to database.
        insert_node = func_insert_node( sim_id, tool_id, node )

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

    # Start session.
    s = session()

    try:
        # Retrieve the simulation ID.
        sim_query = s.query( Simulation ).filter_by( name = simulation_name ).one()
        sim_id = sim_query.id

        # Retrieve information about nodes, ports and links belonging to the simulation ID.
        links = s.query( PortConnectionExt ).filter_by( simulation_id = sim_id ).all()
        nodes = s.query( Node ).filter_by( simulation_id = sim_id ).all()

        # Add nodes.
        for n in nodes:
            # Get data stored for simulation tool.
            sim_tool_data = s.query( SimulationTool ).filter_by( id = n.tool_id ).one()

            # Get additional data (generic parameters) for simulation tool.
            sim_tool_param_data = s.query( GenericParameterTool ).filter_by( tool_id = n.tool_id ).all()

            # Convert database information into dict.
            sim_tool_param = retrieve_generic_parameters( sim_tool_param_data )

            # Check if optional parameter 'command' is present.
            sim_tool_command = None
            if 'command' in sim_tool_param:
                sim_tool_command = sim_tool_param['command']

            # Check if optional parameter 'files' is present.
            sim_tool_files = None
            if 'files' in sim_tool_param:
                # Split comma-separated string into list of strings.
                sim_tool_files = sim_tool_param['files'].split( __separator__ )

            # Define simulation tool.
            sim_tool = _scenario.SimulationTool( name = sim_tool_data.name, model = sim_tool_param['model'], image = sim_tool_param['image'], wrapper = sim_tool_param['wrapper'], command = sim_tool_command, files = sim_tool_files )

            scenario.create_and_add_node( n.name, sim_tool )

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


def write_sim_tool_to_db( sim_tool, session ):
    # Define function call to insert simulation tool into database.
    insert_sim_tool = func_insert_tool( sim_tool.name )

    # Store simulation tool and retrieve the ID of its database representation.
    result = session.query( insert_sim_tool ).one()
    tool_id = result[0]

    # Store 'model' attribute as generic parameter.
    insert_model = func_insert_string_parameter_tool( tool_id, 'model', sim_tool.model )
    result = session.query( insert_model ).one()

    # Store 'image' attribute as generic parameter.
    insert_image = func_insert_string_parameter_tool( tool_id, 'image', sim_tool.image )
    result = session.query( insert_image ).one()

    # Store 'wrapper' attribute as generic parameter.
    insert_wrapper = func_insert_string_parameter_tool( tool_id, 'wrapper', sim_tool.wrapper )
    result = session.query( insert_wrapper ).one()

    # Store 'command' attribute as generic parameter.
    if sim_tool.command is not None:
        insert_command = func_insert_string_parameter_tool( tool_id, 'command', sim_tool.command )
        result = session.query( insert_command ).one()

    # Store 'files' attribute as generic parameter.
    if sim_tool.files is not None:
        # Convert list of strings to comma-separated string.
        str_files = __separator__.join( map( str, sim_tool.files ) )
        # Now store it as string.
        insert_files = func_insert_string_parameter_tool( tool_id, 'files', str_files )
        result = session.query( insert_files ).one()

    return tool_id


def retrieve_generic_parameters( generic_param_data ):
    # Create dict of parameters.
    generic_param = {}

    # Check which field of the data is present and fill the dict accordingly.
    for data in generic_param_data:
        if data.strval is not None:
            generic_param[data.name] = data.strval
        elif data.intval is not None:
            generic_param[data.name] = data.intval
        elif data.realval is not None:
            generic_param[data.name] = data.realval
        elif data.arrayval is not None:
            generic_param[data.name] = data.arrayval
        elif data.urival is not None:
            generic_param[data.name] = data.urival
        elif data.dateval is not None:
            generic_param[data.name] = data.dateval

    # Return dict.
    return generic_param


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
