from sqlalchemy.sql import func


### For some reason this function does not work ...
def func_cleanup_schema():
    """
    Define function call to clean-up schema.
    """
    return func.sim_pkg.cleanup_schema().execution_options( autocommit = True )


def func_insert_simulation( scenario ):
    """
    Define function call to insert simulation to database.
    """
    return func.sim_pkg.insert_simulation(
        None, # id (integer)
        None, # gmlid (character varying)
        None, # gmlid_codespace (character varying)
        scenario.scenario_name, # name (character varying)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # time_start (timestamp with time zone)
        None, # time_stop (timestamp with time zone)
        None, # time_interval (numeric)
        None, # time_interval_unit (character varying)
        None, # creator_name (character varying)
        None  # creation_date (date)
        )


def func_insert_node( sim_id, tool_id, node, template_node_id = None ):
    """
    Define function call to insert node to database.
    """
    if not isinstance( sim_id, int ):
        raise TypeError( 'parameter \'sim_id\' must be of type \'int\'' )

    if not isinstance( tool_id, int ):
        raise TypeError( 'parameter \'tool_id\' must be of type \'int\'' )

    if template_node_id is not None and not isinstance( template_node_id, int ):
        raise TypeError( 'parameter \'template_node_id\' must be of type \'int\'' )

    return func.sim_pkg.insert_node(
        sim_id, # simulation_id (integer)
        None, # id (integer)
        template_node_id, # parent_id (integer)
        None, # gmlid (varchar)
        None, # gmlid_codespace (varchar)
        node.node_name, # name (character varying)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # cityobject_id (integer)
        tool_id # tool_id (integer)
        )


def func_insert_port( node_id, type, port_name ):
    """
    Define function call to insert input port to database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    return func.sim_pkg.insert_port(
        type, # type (character varying)
        node_id, # node_id (integer)
        None, # id (integer)
        None, # gmlid (character varying)
        None, # gmlid_codespace (character varying)
        port_name, # name (character varying)
        None, # name_codespace (character varying)
        port_name, # variable_name (character varying)
        None, # variable_type (character varying)
        None, # cityobject_id (integer)
        None  # description (text)
        )


def func_insert_port_connection( sim_id, link_name, from_port_id, to_port_id ):
    """
    Define function call to insert link to database.
    """
    if not isinstance( sim_id, int ):
        raise TypeError( 'parameter \'sim_id\' must be of type \'int\'' )

    if not isinstance( link_name, str ):
        raise TypeError( 'parameter \'link_name\' must be of type \'str\'' )

    if not isinstance( from_port_id, int ):
        raise TypeError( 'parameter \'from_port_id\' must be of type \'int\'' )

    if not isinstance( to_port_id, int ):
        raise TypeError( 'parameter \'to_port_id\' must be of type \'int\'' )

    return func.sim_pkg.insert_port_connection(
        from_port_id, # output_port_id (integer)
        to_port_id, # input_port_id (integer)
        sim_id, # simulation_id (integer)
        None, # id (integer)
        None, # gmlid (character varying)
        None, # gmlid_codespace (character varying)
        link_name, # name (character varying)
        None, # name_codespace (character varying)
        None  # description (text)
        )


def func_insert_tool( name ):
    """
    Define function call to insert simulation tool to database.
    """
    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    return func.sim_pkg.insert_tool(
        None, # id (integer)
        None, # gmlid (character varying)
        None, # gmlid_codespace (character varying)
        name, # name (character varying)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # server_name (character varying)
        None, # server_address (character varying)
        None, # os_type (character varying)
        None, # os_version (character varying)
        None, # dependencies (character varying)
        None, # connection_parameters (character varying)
        None, # creator_name (character varying)
        None # creation_date (date)
        )


def func_insert_real_parameter_tool( tool_id, name, value, unit = None ):
    """
    Define function call to insert real parameter associated to simulation tool into database.
    """
    if not isinstance( tool_id, int ):
        raise TypeError( 'parameter \'tool_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, float ):
        raise TypeError( 'parameter \'value\' must be of type \'float\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # strval (character varying)
        None, # intval (integer)
        value, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        tool_id, # tool_id (integer)
        None, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_integer_parameter_tool( tool_id, name, value, unit = None ):
    """
    Define function call to insert integer parameter associated to simulation tool into database.
    """
    if not isinstance( tool_id, int ):
        raise TypeError( 'parameter \'tool_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, int ):
        raise TypeError( 'parameter \'value\' must be of type \'int\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # strval (character varying)
        value, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        tool_id, # tool_id (integer)
        None, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_string_parameter_tool( tool_id, name, value ):
    """
    Define function call to insert string parameter associated to simulation tool into database.
    """
    if not isinstance( tool_id, int ):
        raise TypeError( 'parameter \'tool_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        None, # description (text)
        value, # strval (character)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        None, # unit (character varying)
        tool_id, # tool_id (integer)
        None, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_array_parameter_tool( tool_id, name, value, unit = None ):
    """
    Define function call to insert array parameter associated to simulation tool into database.
    """
    if not isinstance( tool_id, int ):
        raise TypeError( 'parameter \'tool_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not ( isinstance( value, list ) and all( isinstance( elem, float ) for elem in value ) ):
        raise TypeError( 'parameter \'value\' must be of type \'list of float\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        value, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        tool_id, # tool_id (integer)
        None, # node_id (integer)
        None, # simulation_id (integer)
        )
