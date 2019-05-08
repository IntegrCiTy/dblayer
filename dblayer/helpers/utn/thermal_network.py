# Helper functions for the Utility Network ADE and generic attributes.
from dblayer.helpers.utn.feature import *
from dblayer.helpers.generic_attributes import *

# SQL functions for inserting Energy ADE objects into the database.
from dblayer.func.func_citydb_view_nrg import *

# Other imports.
from collections import namedtuple


class ThermalNodeData(
    namedtuple(
        'ThermalNodeData_Tuple',
        ['feature_id', 'feature_graph_id', 'node_id', 'posx', 'posy']
        )
    ):
    """
    Data structure for collecting information about thermal node data that will be stored in the 3DCityDB:

    Attributes:

    feature_id (int): ID of the network feature associated to the thermal node

    feature_graph_id (int):  ID of the network feature graph associated to the thermal node

    node_id: ID of the single node contained in the network feature graph

    posx, posy (float): 2D coordinates of the thermal node
    """

    __slots__ = ()


def write_network_to_db(
    db_access,
    name,
    temperature_range_from = None,
    temperature_range_to = None,
    temperature_range_unit = None,
    flow_rate_range_from = None,
    flow_rate_range_to = None,
    flow_rate_range_unit = None,
    pressure_range_from = None,
    pressure_range_to = None,
    pressure_range_unit = None,
    id = None
    ):
    """
    Insert a new empty thermal network (type 'Network') into the 3DCityDB. Automatically adds a commodity description (type 'LiquidMedium') and an empty network graph (type 'NetworkGraph').

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the bus (string)
    :param temperature_range_from: lower temperature range (optional, float)
    :param temperature_range_to: upper temperature range (optional, float)
    :param temperature_range_unit: temperature range unit (optional, string)
    :param flow_rate_range_from: lower flow rate range (optional, float)
    :param flow_rate_range_to: upper flow rate range (optional, float)
    :param flow_rate_range_unit: flow_rate range unit (optional, string)
    :param pressure_range_from: lower pressure range (optional, float)
    :param pressure_range_to: upper pressure range (optional, float)
    :param pressure_range_unit: pressure range unit (optional, string)
    :param id: the network ID can be specified explicitely, otherwise an ID will be assigned automatically (optional, int)

    :return (ntw_id, ntw_graph_id): network ID and network graph ID (tuple of int)
    """

    commodity_id = db_access.add_citydb_object(
        insert_commodity_liquid_medium,
        name = name + '_commodity',
        type = 'districtHeatingWater',
        temperature_range_from = temperature_range_from,
        temperature_range_to = temperature_range_to,
        temperature_range_unit = temperature_range_unit,
        flow_rate_range_from = flow_rate_range_from,
        flow_rate_range_to = flow_rate_range_to,
        flow_rate_range_unit = flow_rate_range_unit,
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


def write_dhw_sink_to_db(
    db_access,
    name,
    coord,
    heat_diss_tot_value,
    heat_diss_tot_value_unit,
    spatial_reference_id,
    network_id,
    network_graph_id ):
    """
    Inserts an electrical load into the 3DCityDB.

    This function adds an object of type 'ElectricalAppliance' to the database, which stores the (static) power consumption. This is done with the help of function 'add_citydb_object', which in turn uses function 'insert_electrical_appliances'. The reactive power 'q_kvar' is associated as generic parameter to this object.

    Furthermore, a terminal element is added to the network using function 'write_terminal_element_to_db', which is linked to the electrical appliance via its city object ID.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the load (string)
    :param coord: 2D coordinates of bus (dblayer.func.func_postgis_geom.Point2D)
    :param heat_diss_tot_value: total heat dissipation (float)
    :param heat_diss_tot_value_unit: unit of total heat dissipation (string)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: instance of class ThermalNodeData (dblayer.helpers.utn.thermal_network.ThermalNodeData)
    """

    appliance_id = db_access.add_citydb_object(
        insert_dhw_facilities,
        name = 'dhw_facility_' + name,
        heat_diss_tot_value = heat_diss_tot_value,
        heat_diss_tot_value_unit = heat_diss_tot_value_unit
    )

    node = write_terminal_element_to_db(
        db_access,
        name,
        coord,
        'thermal-sink',
        spatial_reference_id,
        network_id,
        network_graph_id,
        cityobject_id = appliance_id
        )

    return node


def write_junction_to_db(
    db_access,
    name,
    coord,
    spatial_reference_id,
    network_id,
    network_graph_id
    ):
    """
    Insert a junction for two or more pipes into the 3DCityDB.

    This function relies on the helper function 'insert_ntw_feature_2dpoint', which adds a new newtwork feature, represented by a 2D point. In addition to the new network feature, a feature graph containing a single exterior node is created.

    Function 'insert_ntw_feature_2dpoint' in turn uses function 'insert_ntw_feat_distrib_elem_pipe_other_shape', which means that the connector will be added to the 3DCityDB as a network feature of type 'OtherShapePipe'.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the connector (string)
    :param coord: 2D coordinates of bus (dblayer.func.func_postgis_geom.Point2D)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: instance of class ThermalNodeData (dblayer.helpers.utn.thermal_network.ThermalNodeData)
    """

    (feature_id, feature_graph_id, node_id) = insert_ntw_feature_2dpoint(
        db_access,
        insert_ntw_feat_distrib_elem_pipe_other_shape,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        coord,
        class_name = 'junction'
    )

    return ThermalNodeData( feature_id, feature_graph_id, node_id, coord.x, coord.y )


def write_terminal_element_to_db(
    db_access,
    name,
    coord,
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
    :param coord: 2D coordinates of bus (dblayer.func.func_postgis_geom.Point2D)
    :param terminal_type: type of terminal element (string)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this terminal element will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this terminal element will be added in the 3DCityDB (int)
    :param cityobject_id: ID of associated city object (int, optional)

    :return: instance of class ThermalNodeData (dblayer.helpers.utn.thermal_network.ThermalNodeData)
    """

    (feature_id, feature_graph_id, node_id) = insert_ntw_feature_2dpoint(
        db_access,
        insert_ntw_feat_term_elem,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        coord,
        class_name = terminal_type,
        cityobject_id = cityobject_id
    )

    return ThermalNodeData( feature_id, feature_graph_id, node_id, coord.x, coord.y )


def write_round_pipe_to_db(
    db_access,
    name,
    from_node,
    to_node,
    spatial_reference_id,
    network_id,
    network_graph_id,
    pipe_type = None,
    ext_diameter = None,
    ext_diameter_unit = None,
    int_diameter = None,
    int_diameter_unit = None
    ):
    """
    Insert a n electrical line into the 3DCityDB.

    This function uses function 'insert_and_link_ntw_feature_2dlinestring', whichh adds a new newtwork feature represented by a 2D line segment (made up of 2D points). In addition to the new network feature, a feature graph containing a 2D line segment is created and the start and end points of this line segment are associated to exterior nodes and linked via an interior feature link.

    Function 'insert_and_link_ntw_feature_2dlinestring' in turn uses function 'insert_ntw_feat_distrib_elem_pipe_round', which means that a network feature of type 'RoundPipe' will be added to the 3DCityDB.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of line (string)
    :param from_node: information about the thermal node this line is connected to (dblayer.helpers.utn.electrical_network.ThermalNodeData)
    :param to_node: information about the thermal node this line is connected to (dblayer.helpers.utn.electrical_network.ThermalNodeData)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this pipe will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this pipe will be added in the 3DCityDB (int)
    :param pipe_type: type of pipe (string)
    :param ext_diameter: external diameter of the pipe (float, optional)
    :param ext_diameter_unit: unit of the external diameter of the pipe (string, optional)
    :param int_diameter: internal diameter of the pipe (float, optional)
    :param int_diameter_unit: unit of the internal diameter of the pipe (string, optional)

    :return: None
    """

    line_segment = [
        Point2D(from_node.posx, from_node.posy),
        Point2D(to_node.posx, to_node.posy)
    ]

    ( feature_id, feature_graph_id, start_node_id, end_node_id, 
        start_inter_feature_link_id, end_inter_feature_link_id, interior_feature_link_id ) = \
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
        class_name = pipe_type,
        ext_diameter = ext_diameter,
        ext_diameter_unit = ext_diameter_unit,
        int_diameter = int_diameter,
        int_diameter_unit = int_diameter_unit
    )

