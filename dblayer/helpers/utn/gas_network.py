# Helper functions for the Utility Network ADE and generic attributes.
from dblayer.helpers.utn.feature import *
from dblayer.helpers.generic_attributes import *

# SQL functions for inserting Energy ADE objects into the database.
from dblayer.func.func_citydb_view_nrg import *

# Other imports.
from collections import namedtuple


class GasNetworkNodeData(
    namedtuple(
        'GasNetworkNodeData_Tuple',
        ['feature_id', 'feature_graph_id', 'node_id', 'posx', 'posy']
        )
    ):
    """
    Data structure for collecting information about gas network node data that will be stored in the 3DCityDB:

    Attributes:

    feature_id (int): ID of the network feature associated to the gas network node

    feature_graph_id (int):  ID of the network feature graph associated to the gas network node

    node_id: ID of the single node contained in the network feature graph

    posx, posy (float): 2D coordinates of the gas network node
    """

    __slots__ = ()


def write_network_to_db(
    db_access,
    name,
    pressure_range_from = None,
    pressure_range_to = None,
    pressure_range_unit = None,
    id = None
    ):
    """
    Insert a new empty natural gas network (type 'Network') into the 3DCityDB. Automatically adds a commodity description (type 'GaseousMedium') and an empty network graph (type 'NetworkGraph').

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the bus (string)
    :param pressure_range_from: lower pressure range (optional, float)
    :param pressure_range_to: upper pressure range (optional, float)
    :param pressure_range_unit: pressure range unit (optional, string)
    :param id: the network ID can be specified explicitely, otherwise an ID will be assigned automatically (optional, int)

    :return (ntw_id, ntw_graph_id): network ID and network graph ID (tuple of int)
    """

    commodity_id = db_access.add_citydb_object(
        insert_commodity_gaseous_medium,
        name = name + '_commodity',
        type = 'naturalGas',
        pressure_range_from = pressure_range_from,
        pressure_range_to = pressure_range_to,
        pressure_range_unit = pressure_range_unit,
        )

    ntw_id = db_access.add_citydb_object(
        insert_network,
        name = name,
        id = id,
        commodity_id = commodity_id
        )

    ntw_graph_id = db_access.add_citydb_object(
        insert_network_graph,
        name = name + '_graph',
        network_id = ntw_id
        )

    return ( ntw_id, ntw_graph_id )


def write_network_node_to_db(
    db_access,
    name,
    level,
    coord,
    spatial_reference_id,
    network_id,
    network_graph_id
    ):
    """
    Insert a node of a gas network into the 3DCityDB.

    This function relies on the helper function 'insert_ntw_feature_2dpoint', which adds a new newtwork feature, represented by a 2D point. In addition to the new network feature, a feature graph containing a single exterior node is created.

    Function 'insert_ntw_feature_2dpoint' in turn uses function 'insert_ntw_feat_distrib_elem_pipe_other_shape', which means that the connector will be added to the 3DCityDB as a network feature of type 'OtherShapePipe'.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the connector (string)
    :param level: pressure level (string)
    :param coord: 2D coordinates of bus (dblayer.func.func_postgis_geom.Point2D)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: instance of class GasNetworkNodeData (dblayer.helpers.utn.thermal_network.GasNetworkNodeData)
    """

    (feature_id, feature_graph_id, node_id) = insert_ntw_feature_2dpoint(
        db_access,
        insert_ntw_feat_distrib_elem_pipe_other_shape,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        coord,
        class_name = 'gas-network-node',
        function_of_line = level
        )

    return GasNetworkNodeData( feature_id, feature_graph_id, node_id, coord.x, coord.y )


def write_gas_sink_to_db(
    db_access,
    name,
    connected_node,
    gas_consumption,
    gas_consumption_unit,
    spatial_reference_id,
    network_id,
    network_graph_id,
    cityobject_id = None
    ):
    """
    Inserts a gas sink into the 3DCityDB.

    This function adds an object of type 'TerminalElement' to the database, which stores the (static) gas consumption as generic attributes. This is done with the help of function 'write_terminal_element_to_db'.

    Furthermore, function 'add_generic_attributes' is used to add the generic attributes 'gas_consumption' and 'gas_consumption_unit' for this gas sink.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the load (string)
    :param connected_node: information about the network node this terminal element is connected to (dblayer.helpers.utn.gas_network.GasNetworkNodeData)
    :param gas_consumption: total gas consumption (float)
    :param gas_consumption_unit: unit of total gas consumption (string)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)
    :param cityobject_id: ID of associated city object (int, optional)

    :return: instance of class GasNetworkNodeData (dblayer.helpers.utn.thermal_network.GasNetworkNodeData)
    """

    node = write_terminal_element_to_db(
        db_access,
        name,
        connected_node,
        'gas-network-sink',
        spatial_reference_id,
        network_id,
        network_graph_id,
        cityobject_id = cityobject_id
        )

    add_generic_attributes(
        db_access,
        node.feature_id,
        { 'gas_consumption': gas_consumption }
        )

    add_generic_attributes(
        db_access,
        node.feature_id,
        { 'gas_consumption_unit': gas_consumption_unit }
        )


def write_feeder_to_db(
    db_access,
    name,
    connected_node,
    p_lim_kw,
    p_pa,
    spatial_reference_id,
    network_id,
    network_graph_id
    ):
    """
    Inserts a gas sink into the 3DCityDB.

    This function adds an object of type 'TerminalElement' to the database, which stores the (static) gas consumption as generic attributes. This is done with the help of function 'write_terminal_element_to_db'.

    Furthermore, function 'add_generic_attributes' is used to add the generic attributes 'gas_consumption' and 'gas_consumption_unit' for this gas sink.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the load (string)
    :param connected_node: information about the network node this terminal element is connected to (dblayer.helpers.utn.gas_network.GasNetworkNodeData)
    :param p_lim_kw: maximum power in kW flowing through the feeder (float)
    :param p_pa: operating pressure level in Pa at the output of the feeder (float)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: instance of class GasNetworkNodeData (dblayer.helpers.utn.thermal_network.GasNetworkNodeData)
    """

    node = write_terminal_element_to_db(
        db_access,
        name,
        connected_node,
        'gas-network-feeder',
        spatial_reference_id,
        network_id,
        network_graph_id
        )

    add_generic_attributes(
        db_access,
        node.feature_id,
        { 'p_lim_kw': p_lim_kw }
        )

    add_generic_attributes(
        db_access,
        node.feature_id,
        { 'p_pa': p_pa }
        )


def write_terminal_element_to_db(
    db_access,
    name,
    connected_node,
    terminal_type,
    spatial_reference_id,
    network_id,
    network_graph_id,
    cityobject_id = None
    ):
    """
    Insert a terminal element into the 3DCityDB.

    This function calls function 'insert_ntw_feature_2dpoint' and in addition connects the generated exterior node via an inter feature link to another exterior node.

    Function 'insert_and_link_ntw_feature_2dpoint' in turn uses function 'insert_ntw_feat_term_elem', which means that a network feature of type 'TerminalElement' will be added to the 3DCityDB.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the terminal element (string)
    :param connected_node: information about the network node this terminal element is connected to (dblayer.helpers.utn.gas_network.GasNetworkNodeData)
    :param terminal_type: type of terminal element (string)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this terminal element will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this terminal element will be added in the 3DCityDB (int)
    :param cityobject_id: ID of associated city object (int, optional)

    :return: None
    """

    ( feature_id, feature_graph_id, node_id, inter_feature_link_id ) = \
    insert_and_link_ntw_feature_2dpoint(
        db_access,
        insert_ntw_feat_term_elem,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        Point2D( connected_node.posx, connected_node.posy ),
        connected_node.node_id,
        class_name = terminal_type,
        cityobject_id = cityobject_id
        )

    return GasNetworkNodeData(
        feature_id, feature_graph_id, node_id,
        connected_node.posx, connected_node.posy
        )


def write_round_pipe_to_db(
    db_access,
    name,
    from_node,
    to_node,
    spatial_reference_id,
    network_id,
    network_graph_id,
    ext_diameter = None,
    ext_diameter_unit = None,
    int_diameter = None,
    int_diameter_unit = None,
    cur_flow_rate = None,
    cur_flow_rate_unit = None,
    cur_status = None,
    pot_flow_rate = None,
    pot_flow_rate_unit = None,
    pot_status = None
    ):
    """
    Insert a n electrical line into the 3DCityDB.

    This function uses function 'insert_and_link_ntw_feature_2dlinestring', whichh adds a new newtwork feature represented by a 2D line segment (made up of 2D points). In addition to the new network feature, a feature graph containing a 2D line segment is created and the start and end points of this line segment are associated to exterior nodes and linked via an interior feature link.

    Function 'insert_and_link_ntw_feature_2dlinestring' in turn uses function 'insert_ntw_feat_distrib_elem_pipe_round', which means that a network feature of type 'RoundPipe' will be added to the 3DCityDB.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of line (string)
    :param from_node: information about the thermal node this line is connected to (dblayer.helpers.utn.electrical_network.GasNetworkNodeData)
    :param to_node: information about the thermal node this line is connected to (dblayer.helpers.utn.electrical_network.GasNetworkNodeData)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this pipe will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this pipe will be added in the 3DCityDB (int)
    :param pipe_type: type of pipe (string)
    :param ext_diameter: external diameter of the pipe (float, optional)
    :param ext_diameter_unit: unit of the external diameter of the pipe (string, optional)
    :param int_diameter: internal diameter of the pipe (float, optional)
    :param int_diameter_unit: unit of the internal diameter of the pipe (string, optional)
    :param cur_flow_rate: current flow rate of medium (float, optional)
    :param cur_flow_rate_unit: unit of current flow rate (float, optional)
    :param cur_status = current status (string, optional)
    :param pot_flow_rate: supposed flow rate of medium (float, optional)
    :param pot_flow_rate_unit: unit of supposed flow rate (float, optional)
    :param pot_status = supposed status (string, optional)

    :return: None
    """

    line_segment = [
        Point2D(from_node.posx, from_node.posy),
        Point2D(to_node.posx, to_node.posy)
        ]

    ( feature_id, feature_graph_id, start_node_id, end_node_id,
        start_inter_feature_link_id, end_inter_feature_link_id,
        interior_feature_link_id ) = \
    insert_and_link_ntw_feature_2dlinestring(
        db_access,
        insert_ntw_feat_distrib_elem_pipe_round,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        line_segment,
        from_node.node_id,
        to_node.node_id,
        class_name = 'gas-network-pipe',
        ext_diameter = ext_diameter,
        ext_diameter_unit = ext_diameter_unit,
        int_diameter = int_diameter,
        int_diameter_unit = int_diameter_unit
        )

    db_access.add_citydb_object(
        insert_medium_supply_gaseous,
        type = 'naturalGas',
        cur_flow_rate = cur_flow_rate,
        cur_flow_rate_unit = cur_flow_rate_unit,
        cur_status = cur_status,
        pot_flow_rate = pot_flow_rate,
        pot_flow_rate_unit = pot_flow_rate_unit,
        pot_status = pot_status,
        cityobject_id = feature_id,
        )



def write_station_to_db(
    db_access,
    name,
    from_node,
    to_node,
    p_lim_kw,
    p_pa,
    spatial_reference_id,
    network_id,
    network_graph_id):
    """
    Inserts a gas station into the 3DCityDB.

    This function uses function 'insert_and_link_ntw_feature_2dlinestring', which in turn uses function 'insert_ntw_feat_complex_funct_elem' to represent the station in the 3DCityDB as an object of type 'ComplexFunctionalElement'.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of station (string)
    :param from_node: information about the network node this station is connected to (dblayer.helpers.utn.gas_network.GasNetworkNodeData)
    :param to_node: information about the network node this station is connected to (dblayer.helpers.utn.gas_network.GasNetworkNodeData)
    :param p_lim_kw: maximum power in kW flowing through the station (float)
    :param p_pa: operating pressure level in Pa at the output of the station (float)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this station will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this station will be added in the 3DCityDB (int)

    :return: None
    """

    line_segment = [
        Point2D(from_node.posx, from_node.posy),
        Point2D(to_node.posx, to_node.posy)
        ]

    ( feature_id, feature_graph_id, start_node_id, end_node_id,
        start_inter_feature_link_id, end_inter_feature_link_id,
        interior_feature_link_id ) = \
    insert_and_link_ntw_feature_2dlinestring(
        db_access,
        insert_ntw_feat_complex_funct_elem,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        line_segment,
        from_node.node_id,
        to_node.node_id,
        class_name = 'gas-network-station'
        )

    add_generic_attributes(
        db_access,
        feature_id,
        { 'p_lim_kw': p_lim_kw }
        )

    add_generic_attributes(
        db_access,
        feature_id,
        { 'p_pa': p_pa }
        )
