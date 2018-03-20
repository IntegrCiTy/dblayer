from . import scenario as _scenario
import json


def dump_to_json_string( scenario ):
    """
    Dump scenario to JSON-formatted string (e.g., to be used as input for OBNL). Returns a string.
    """
    # Check if parameter 'scenario' is of correct type (Scenario).
    if not isinstance( scenario, _scenario.Scenario ):
        raise TypeError( 'parameter \'scenario\' must be of type \'Scenario\'' )

    # Dictionary for collecting and writing all information regarding the scenario's nodes.
    write_nodes = {}

    # Iterate through the scenario's nodes.
    for node_name, node in scenario.nodes.items():
        # Retrieve the names of the input/output variables associated to the ports of the node.
        write_inputs = list( node.input_ports.keys() )
        write_outputs = list( node.output_ports.keys() )

        # Write to dictionary.
        write_nodes[ node_name ] = { 'inputs' : write_inputs, 'outputs' : write_outputs }

    # Dictionary for collecting and writeing all information regarding the scenario's links.
    write_links = {}

    # Iterate through the scenario's links.
    for link_name, link in scenario.links.items():
        # Retrieve information about the link's input port: variable name and node name
        write_from_node_name = link.output_port.node.node_name
        write_from_node_var = link.output_port.variable_name
        write_from_node = { 'node' : write_from_node_name, 'attr' : write_from_node_var }

        # Retrieve information about the link's output port: variable name and node name
        write_to_node_name = link.input_port.node.node_name
        write_to_node_var = link.input_port.variable_name
        write_to_node = { 'node' : write_to_node_name, 'attr' : write_to_node_var }

        # Write to dictionary.
        write_links[ link_name ] = { 'out' : write_from_node, 'in' : write_to_node }

    # Complete information about the scenario in form of a single dictionary.
    write_scenario = { 'nodes' : write_nodes, 'links' : write_links }

    # Return JSON representation of the scenario as string.
    return json.dumps( write_scenario, sort_keys = False, indent = 2, separators = ( ',', ': ' ) )


def dump_to_json_file( scenario, file_name ):
    """
    Dump scenario to JSON-formatted file.
    """
    # Check if parameter 'scenario' is of correct type (Scenario).
    if not isinstance( scenario, _scenario.Senario ):
        raise TypeError( 'parameter \'scenario\' must be of type \'Scenario\'' )

    # Check if parameter 'file_name' is of correct type (str).
    if not isinstance( file_name, str ):
        raise TypeError( 'parameter \'file_name\' must be of type \'str\'' )

    # Dump scenario to string.
    json_string = dump_to_json_string( scenario )

    # Write dump to file.
    file = open( file_name, 'w')
    file.write( json_string )
    file.close()


def read_from_json_string( json_string, scenario_name ):
    """
    Read string in JSON format and create scenario. Returns scenario.
    """
    # Check if parameter 'json_string' is of correct type (str).
    if not isinstance( json_string, str ):
        raise TypeError( 'parameter \'json_string\' must be of type \'str\'' )

    # Check if parameter 'scenario_name' is of correct type (str).
    if not isinstance( scenario_name, str ):
        raise TypeError( 'parameter \'scenario_name\' must be of type \'str\'' )

    # Decode JSON string into data structure.
    read_scenario = json.loads( json_string )

    # Check if data structure defines keys 'nodes' and 'links'.
    if not ( ( 'nodes' in read_scenario ) and ( 'links' in read_scenario ) ):
        raise RuntimeError( 'JSON string invalid' )

    # Create scenario.
    scenario = _scenario.Scenario( scenario_name )

    # Add nodes.
    read_nodes = read_scenario[ 'nodes' ]
    for node_name, node_data in read_nodes.items():
        input_variable_names = node_data[ 'inputs' ] if ( 'inputs' in node_data ) else []
        output_variable_names = node_data[ 'outputs' ] if ( 'outputs' in node_data ) else []
        scenario.create_and_add_node( node_name, input_variable_names, output_variable_names )

    # Add links.
    read_links = read_scenario[ 'links' ]
    for link_name, link_data in read_links.items():
        from_node_name = link_data[ 'out' ][ 'node' ]
        from_node_var = link_data[ 'out' ][ 'attr' ]
        to_node_name = link_data[ 'in' ][ 'node' ]
        to_node_var = link_data[ 'in' ][ 'attr' ]
        scenario.create_and_add_link( link_name, from_node_name, from_node_var, to_node_name, to_node_var )

    # Return the scenario.
    return scenario


def read_from_json_file( file_name, scenario_name ):
    """
    Read JSON-formatted file and create scenario. Returns scenario.
    """
    # Check if parameter 'file_name' is of correct type (str).
    if not isinstance( file_name, str ):
        raise TypeError( 'parameter \'json_string\' must be of type \'str\'' )

    # Check if parameter 'scenario_name' is of correct type (str).
    if not isinstance( scenario_name, str ):
        raise TypeError( 'parameter \'scenario_name\' must be of type \'str\'' )

    # Open JSON-formatted file.
    file = open( 'test.json' )

    # Load content from file as string.
    json_string = file.read()

    # Read the scenario from JSON string.
    scenario = read_from_json_string( json_string, scenario_name )

    # Close the file.
    file.close()

    # Return the scenario.
    return scenario
