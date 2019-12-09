from sqlalchemy.sql import func

import warnings

from urllib.parse import urlparse
import os.path


### For some reason this function does not work ...
def func_cleanup_schema():
    """
    Define function call to clean-up schema.
    """
    return func.sim_pkg.cleanup_schema().execution_options( autocommit = True )


def func_insert_simulation( sim_name ):
    """
    Define function call to insert simulation into the database.
    """
    return func.sim_pkg.insert_simulation(
        None, # id (integer)
        None, # gmlid (character varying)
        None, # gmlid_codespace (character varying)
        sim_name, # name (character varying)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # time_start (timestamp with time zone)
        None, # time_stop (timestamp with time zone)
        None, # time_interval (numeric)
        None, # time_interval_unit (character varying)
        None, # creator_name (character varying)
        None  # creation_date (date)
        )


def func_insert_node( node_name, sim_id, tool_id, template_node_id = None ):
    """
    Define function call to insert node into the database.
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
        node_name, # name (character varying)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # cityobject_id (integer)
        tool_id # tool_id (integer)
        )


def func_insert_node_template( node_name ):
    """
    Define function call to insert a template node into the database.
    """
    if not isinstance( node_name, str ):
        raise TypeError( 'parameter \'node_name\' must be of type \'str\'' )

    return func.sim_pkg.insert_node_template(
        None, # simulation_id (integer)
        None, # id (integer)
        None, # parent_id (integer)
        None, # gmlid (varchar)
        None, # gmlid_codespace (varchar)
        node_name, # name (character varying)
        None, # name_codespace (character varying)
        None, # description (text)
        None, # cityobject_id (integer)
        None # tool_id (integer)
        )


def func_insert_port( node_id, type, port_name, port_unit ):
    """
    Define function call to insert input port into the database.
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
        port_unit, # variable_type (character varying)
        None, # cityobject_id (integer)
        None  # description (text)
        )


def func_insert_port_connection( sim_id, link_name, from_port_id, to_port_id ):
    """
    Define function call to insert link into the database.
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
    Define function call to insert simulation tool into the database.
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


def func_insert_real_parameter_tool( tool_id, name, value, unit = None, description = None ):
    """
    Define function call to insert real parameter associated to simulation tool into the database.
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
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
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


def func_insert_integer_parameter_tool( tool_id, name, value, unit = None, description = None ):
    """
    Define function call to insert integer parameter associated to simulation tool into the database.
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
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
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


def func_insert_string_parameter_tool( tool_id, name, value, description = None ):
    """
    Define function call to insert string parameter associated to simulation tool into the database.
    """
    if not isinstance( tool_id, int ):
        raise TypeError( 'parameter \'tool_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
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


def func_insert_array_parameter_tool( tool_id, name, value, unit = None, description = None ):
    """
    Define function call to insert array parameter associated to simulation tool into the database.
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
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
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


def func_insert_uri_parameter_tool( tool_id, name, value, description = None ):
    """
    Define function call to insert URI parameter associated to tool into the database.
    """
    if not isinstance( tool_id, int ):
        raise TypeError( 'parameter \'tool_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    parsed_uri = urlparse( value )

    if parsed_uri.scheme != 'file':
        raise TypeError( 'parameter \'value\' must comply to the file URI scheme' )

    if False == os.path.exists( parsed_uri.path ):
        warnings.warn( 'file does not exist: {}'.format( parsed_uri.path ), RuntimeWarning )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        value, # urival (character varying)
        None, # dateval (timestamp with time zone)
        None, # unit (character varying)
        tool_id, # tool_id (integer)
        None, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_real_parameter_node( node_id, name, value, unit = None, description = None ):
    """
    Define function call to insert real parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, float ):
        raise TypeError( 'parameter \'value\' must be of type \'float\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        value, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_integer_parameter_node( node_id, name, value, unit = None, description = None ):
    """
    Define function call to insert integer parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, int ):
        raise TypeError( 'parameter \'value\' must be of type \'int\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        value, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_string_parameter_node( node_id, name, value, description = None ):
    """
    Define function call to insert string parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        value, # strval (character)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        None, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_array_parameter_node( node_id, name, value, unit = None, description = None ):
    """
    Define function call to insert array parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not ( isinstance( value, list ) and all( isinstance( elem, float ) for elem in value ) ):
        raise TypeError( 'parameter \'value\' must be of type \'list of float\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        value, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_uri_parameter_node( node_id, name, value, description = None ):
    """
    Define function call to insert URI parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    parsed_uri = urlparse( value )

    if parsed_uri.scheme != 'file':
        raise TypeError( 'parameter \'value\' must comply to the file URI scheme' )

    if False == os.path.exists( parsed_uri.path ):
        warnings.warn( 'file does not exist: {}'.format( parsed_uri.path ), RuntimeWarning )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        value, # urival (character varying)
        None, # dateval (timestamp with time zone)
        None, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_real_init_val_node( node_id, name, value, unit = None, description = None ):
    """
    Define function call to insert real parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, float ):
        raise TypeError( 'parameter \'value\' must be of type \'float\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter_init(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        value, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_integer_init_val_node( node_id, name, value, unit = None, description = None ):
    """
    Define function call to insert integer parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, int ):
        raise TypeError( 'parameter \'value\' must be of type \'int\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter_init(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        value, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_string_init_val_node( node_id, name, value, description = None ):
    """
    Define function call to insert string parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        value, # strval (character)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        None, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_array_init_val_node( node_id, name, value, unit = None, description = None ):
    """
    Define function call to insert array parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not ( isinstance( value, list ) and all( isinstance( elem, float ) for elem in value ) ):
        raise TypeError( 'parameter \'value\' must be of type \'list of float\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter_init(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        value, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_object_ref_init_val_node( node_id, name, table_name, object_id, column_name, unit = None, description = None ):
    """
    Define function call to insert array parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( table_name, str ):
        raise TypeError( 'parameter \'table_name\' must be of type \'str\'' )

    if not isinstance( object_id, int ):
        raise TypeError( 'parameter \'object_id\' must be of type \'int\'' )

    if not isinstance( column_name, str ):
        raise TypeError( 'parameter \'column_name\' must be of type \'str\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter_init(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        table_name, # citydb_table_name (character varying)
        object_id, # citydb_object_id (integer)
        column_name, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_generic_attr_ref_init_val_node( node_id, name, attribute_name, attribute_id, unit = None, description = None ):
    """
    Define function call to insert array parameter associated to node into the database.
    """
    if not isinstance( node_id, int ):
        raise TypeError( 'parameter \'node_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( attribute_name, str ):
        raise TypeError( 'parameter \'attribute_name\' must be of type \'str\'' )

    if not isinstance( attribute_id, int ):
        raise TypeError( 'parameter \'attribute_id\' must be of type \'int\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter_init(
        name, # name (character varying)
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        attribute_id, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        attribute_name, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        node_id, # node_id (integer)
        None, # simulation_id (integer)
        )


def func_insert_string_parameter_simulation( sim_id, name, value, description = None ):
    """
    Define function call to insert string parameter associated to simulation into the database.
    """
    if not isinstance( sim_id, int ):
        raise TypeError( 'parameter \'sim_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        value, # strval (character)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        None, # unit (character varying)
        None, # tool_id (integer)
        None, # node_id (integer)
        sim_id, # simulation_id (integer)
        )


def func_insert_array_parameter_simulation( sim_id, name, value, unit = None, description = None ):
    """
    Define function call to insert array parameter associated to node into the database.
    """
    if not isinstance( sim_id, int ):
        raise TypeError( 'parameter \'sim_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not ( isinstance( value, list ) and ( all( isinstance( elem, float ) for elem in value ) or all( isinstance( elem, int ) for elem in value ) ) ):
        raise TypeError( 'parameter \'value\' must be of type \'list of float\' or \'list of int\'' )

    if unit is not None and not isinstance( unit, str ):
        raise TypeError( 'parameter \'unit\' must be of type \'str\'' )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        value, # arrayval (numeric[])
        None, # urival (character varying)
        None, # dateval (timestamp with time zone)
        unit, # unit (character varying)
        None, # tool_id (integer)
        None, # node_id (integer)
        sim_id, # simulation_id (integer)
        )


def func_insert_uri_parameter_simulation( sim_id, name, value, description = None ):
    """
    Define function call to insert URI parameter associated to simulation into the database.
    """
    if not isinstance( sim_id, int ):
        raise TypeError( 'parameter \'sim_id\' must be of type \'int\'' )

    if not isinstance( name, str ):
        raise TypeError( 'parameter \'name\' must be of type \'str\'' )

    if not isinstance( value, str ):
        raise TypeError( 'parameter \'value\' must be of type \'str\'' )

    parsed_uri = urlparse( value )

    if parsed_uri.scheme != 'file':
        raise TypeError( 'parameter \'value\' must comply to the file URI scheme' )

    if False == os.path.exists( parsed_uri.path ):
        warnings.warn( 'file does not exist: {}'.format( parsed_uri.path ), RuntimeWarning )

    return func.sim_pkg.insert_generic_parameter(
        name, # name (character varying)
        None, # is_init_parameter boolean
        None, # id (integer)
        None, # name_codespace (character varying)
        description, # description (text)
        None, # citydb_table_name (character varying)
        None, # citydb_object_id (integer)
        None, # citydb_column_name (character)
        None, # citydb_genericattrib_name (character varying)
        None, # citydb_function (character varying)
        None, # strval (character varying)
        None, # intval (integer)
        None, # realval (numeric)
        None, # arrayval (numeric[])
        value, # urival (character varying)
        None, # dateval (timestamp with time zone)
        None, # unit (character varying)
        None, # tool_id (integer)
        None, # node_id (integer)
        sim_id, # simulation_id (integer)
        )
