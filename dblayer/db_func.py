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


def func_insert_node( sim_id, node ):
    """
    Define function call to insert node to database.
    """
    return func.sim_pkg.insert_node(
        sim_id, # simulation_id (integer)
        None, # id (integer)
        None, # gmlid (character varying)
        None, # gmlid_codespace (character varying)
        node.node_name, # name (character varying)
        None, # name_codespace (character varying)
        None, # description (text)
        None  # cityobject_id (integer)
        )


def func_insert_port( node_id, type, port_name ):
    """
    Define function call to insert input port to database.
    """
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
