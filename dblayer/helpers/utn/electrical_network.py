# Helper functions for the Utility Network ADE and generic attributes.
from dblayer.helpers.utn.feature import *
from dblayer.helpers.generic_attributes import *

# SQL functions for inserting Energy ADE objects into the database.
from dblayer.func.func_citydb_view_nrg import *

# Other imports.
from collections import namedtuple


class BusData(
    namedtuple(
        'BusData_Tuple',
        ['feature_id', 'feature_graph_id', 'node_id', 'posx', 'posy']
        )
    ):
    """
    Data structure for collecting information about bus  data that will be stored in the 3DCityDB:

    Attributes:

    feature_id (int): ID of the network feature associated to the bus

    feature_graph_id (int):  ID of the network feature graph associated to the bus

    node_id: ID of the single node contained in the network feature graph

    posx, posy (float): 2D coordinates of the bus
    """

    __slots__ = ()


def write_network_to_db(
    db_access,
    name,
    type,
    voltage_range_from = None,
    voltage_range_to = None,
    voltage_range_unit = None,
    amperage_range_from = None,
    amperage_range_to = None,
    amperage_range_unit = None,
    id = None
    ) :
    """
    Insert a new empty electrical network (type 'Network') into the 3DCityDB. Automatically adds a commodity description (type 'ElectricalMedium') and an empty network graph (type 'NetworkGraph').

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the bus (string)
    :param type: type of electrical network (string, either one of 'unknown', 'directCurrent', 'singlePhaseAlternatingCurrent', 'threePhaseAlternatingCurrent')
    :param voltage_range_from: lower voltage range (optional, float)
    :param voltage_range_to: upper voltage range (optional, float)
    :param voltage_range_unit: voltage range unit (optional, string)
    :param amperage_range_from: lower amperage range (optional, float)
    :param amperage_range_to: upper amperage range (optional, float)
    :param amperage_range_unit: amperage range unit (optional, string)
    :param id: the network ID can be specified explicitely, otherwise an ID will be assigned automatically (optional, int)

    :return (ntw_id, ntw_graph_id): network ID and network graph ID (tuple of int)
    """

    types = [
        'unknown'
        'directCurrent',
        'singlePhaseAlternatingCurrent',
        'threePhaseAlternatingCurrent'
        ]

    if not type in types:
        raise RuntimeError( 'unknown type of electrical medium: {}'.format( type ) )

    commodity_id = db_access.add_citydb_object(
        insert_commodity_electrical_medium,
        name = name + '_commodity',
        type = type,
        voltage_range_from = voltage_range_from,
        voltage_range_to = voltage_range_to,
        voltage_range_unit = voltage_range_unit,
        amperage_range_from = amperage_range_from,
        amperage_range_to = amperage_range_to,
        amperage_range_unit = amperage_range_unit
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


def write_bus_to_db(
    db_access,
    name,
    type,
    coord,
    vn_kv,
    spatial_reference_id,
    network_id,
    network_graph_id):
    """
    Insert an electrical bus into the 3DCityDB.

    This function relies on the helper function 'insert_ntw_feature_2dpoint', which adds a new newtwork feature, represented by a 2D point. In addition to the new network feature, a feature graph containing a single exterior node is created.

    Function 'insert_ntw_feature_2dpoint' in turn uses function 'insert_ntw_feat_simple_funct_elem', which means that the bus will be added to the 3DCityDB as a network feature of type 'SimpleFunctionalElement'.

    Furthermore, function 'add_generic_attributes' is used to add the generic attribute 'vn_kv' for this bus.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the bus (string)
    :param type: type of bus (string)
    :param coord: 2D coordinates of bus (dblayer.func.func_postgis_geom.Point2D)
    :param vn_kv: grid voltage level in kV (float)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: instance of class BusData (dblayer.helpers.utn.electrical_network.BusData)
    """

    (feature_id, feature_graph_id, node_id) = insert_ntw_feature_2dpoint(
        db_access,
        insert_ntw_feat_simple_funct_elem,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        coord,
        class_name = type
    )

    add_generic_attributes(
        db_access,
        feature_id,
        { 'vn_kv': vn_kv }
    )

    return BusData( feature_id, feature_graph_id, node_id, coord.x, coord.y )


def write_terminal_element_to_db(
    db_access,
    name,
    terminal_type,
    connected_bus,
    spatial_reference_id,
    network_id,
    network_graph_id,
    cityobject_id = None):
    """
    Insert a terminal element into the 3DCityDB.

    This function calls function 'insert_ntw_feature_2dpoint' and in addition connects the generated exterior node via an inter feature link to another exterior node.

    Function 'insert_and_link_ntw_feature_2dpoint' in turn uses function 'insert_ntw_feat_term_elem', which means that a network feature of type 'TerminalElement' will be added to the 3DCityDB.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the terminal element (string)
    :param terminal_type: type of terminal element (string)
    :param connected_bus: information about the bus this terminal element is connected to (dblayer.helpers.utn.electrical_network.BusData)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)
    :param cityobject_id: ID of associated city object (int, optional)

    :return: None
    """

    insert_and_link_ntw_feature_2dpoint(
        db_access,
        insert_ntw_feat_term_elem,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        Point2D( connected_bus.posx, connected_bus.posy ),
        connected_bus.node_id,
        class_name = terminal_type,
        cityobject_id = cityobject_id
    )


def write_line_to_db(
    db_access,
    name,
    from_bus,
    to_bus,
    c_nf_per_km,
    r_ohm_per_km,
    x_ohm_per_km,
    max_i_ka,
    line_type,
    spatial_reference_id,
    network_id,
    network_graph_id):
    """
    Insert an electrical line into the 3DCityDB.

    This function uses function 'insert_and_link_ntw_feature_2dlinestring', whichh adds a new newtwork feature represented by a 2D line segment (made up of 2D points). In addition to the new network feature, a feature graph containing a 2D line segment is created and the start and end points of this line segment are associated to exterior nodes and linked via an interior feature link.

    Function 'insert_and_link_ntw_feature_2dlinestring' in turn uses function 'insert_ntw_feat_distrib_elem_cable', which means that a network feature of type 'Cable' will be added to the 3DCityDB.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of line (string)
    :param from_bus: information about the bus this line is connected to (dblayer.helpers.utn.electrical_network.BusData)
    :param to_bus: information about the bus this line is connected to (dblayer.helpers.utn.electrical_network.BusData)
    :param c_nf_per_km: line capacitance in nF per km (float)
    :param r_ohm_per_km: line resistance in Ohm per km (float)
    :param x_ohm_per_km: line reactance in Ohm per km (float)
    :param max_i_ka: maximum thermal current in kA (float)
    :param line_type: line type (string)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: None
    """

    line_segment = [
        Point2D(from_bus.posx, from_bus.posy),
        Point2D(to_bus.posx, to_bus.posy)
    ]

    ( feature_id, feature_graph_id, start_node_id, end_node_id, start_inter_feature_link_id,
      end_inter_feature_link_id, interior_feature_link_id ) = insert_and_link_ntw_feature_2dlinestring(
        db_access,
        insert_ntw_feat_distrib_elem_cable,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        line_segment,
        from_bus.node_id,
        to_bus.node_id,
        class_name = line_type
    )

    add_generic_attributes(
        db_access,
        feature_id,
        { 'c_nf_per_km': c_nf_per_km, 'r_ohm_per_km': r_ohm_per_km,
          'x_ohm_per_km': x_ohm_per_km, 'max_i_ka': max_i_ka }
    )


def write_switch_to_db(
    db_access,
    name,
    from_bus,
    to_bus,
    switch_type,
    spatial_reference_id,
    network_id,
    network_graph_id):
    """
    Insert a switch into the 3DCityDB.

    This function uses function 'insert_and_link_ntw_feature_2dlinestring', which in turn uses function 'insert_ntw_feat_simple_funct_elem' to represent the switch in the 3DCityDB as an object of type 'SimpleFunctionalElement'.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of switch (string)
    :param from_bus: information about the bus this switch is connected to (dblayer.helpers.utn.electrical_network.BusData)
    :param to_bus: information about the bus this switch is connected to (dblayer.helpers.utn.electrical_network.BusData)
    :param switch_type: type of switch (string)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: None
    """

    line_segment = [
        Point2D(from_bus.posx, from_bus.posy),
        Point2D(to_bus.posx, to_bus.posy)
    ]

    insert_and_link_ntw_feature_2dlinestring(
        db_access,
        insert_ntw_feat_simple_funct_elem,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        line_segment,
        from_bus.node_id,
        to_bus.node_id,
        class_name = 'switch',
        function = switch_type
    )


def write_transformer_to_db(
    db_access,
    name,
    hv_bus,
    lv_bus,
    transformer_type,
    spatial_reference_id,
    network_id,
    network_graph_id):
    """
    Inserts a transformer into the 3DCityDB.

    This function uses function 'insert_and_link_ntw_feature_2dlinestring', which in turn uses function 'insert_ntw_feat_complex_funct_elem' to represent the transformer in the 3DCityDB as an object of type 'ComplexFunctionalElement'.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of transformer (string)
    :param hv_bus: information about the high-voltage bus this transformer is connected to (dblayer.helpers.utn.electrical_network.BusData)
    :param lv_bus: information about the low-voltage bus this transformer is connected to (dblayer.helpers.utn.electrical_network.BusData)
    :param transformer_type: type of transformer (string)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: None
    """

    line_segment = [
        Point2D(hv_bus.posx, hv_bus.posy),
        Point2D(lv_bus.posx, lv_bus.posy)
    ]

    insert_and_link_ntw_feature_2dlinestring(
        db_access,
        insert_ntw_feat_complex_funct_elem,
        spatial_reference_id,
        network_id,
        network_graph_id,
        name,
        line_segment,
        hv_bus.node_id,
        lv_bus.node_id,
        class_name = 'transformer',
        function = transformer_type,
    )



def write_load_to_db(
    db_access,
    name,
    bus,
    p_kw,
    q_kvar,
    spatial_reference_id,
    network_id,
    network_graph_id ):
    """
    Inserts an electrical load into the 3DCityDB.

    This function adds an object of type 'ElectricalAppliance' to the database, which stores the (static) power consumption. This is done with the help of function 'add_citydb_object', which in turn uses function 'insert_electrical_appliances'. The reactive power 'q_kvar' is associated as generic parameter to this object.

    Furthermore, a terminal element is added to the network using function 'write_terminal_element_to_db', which is linked to the electrical appliance via its city object ID.

    :param db_access: instance of class DBAccess, which is the basic interface of package dblayer to interface a 3DCityDB (dblayer.DBAccess)
    :param name: name of the load (string)
    :param p_kw: active power of the load in kW (float)
    :param p_kw: reactive power of the load in kvar (float)
    :param spatial_reference_id: spatial reference ID for the network (int)
    :param network_id: ID of the network, to which the network feature representing this bus will be added in the 3DCityDB (int)
    :param network_graph_id: ID of the network graph, to which the feature graph of this bus will be added in the 3DCityDB (int)

    :return: None
    """

    appliance_id = db_access.add_citydb_object(
        insert_electrical_appliances,
        name = 'electrical_appliance_' + name,
        electr_pwr = p_kw,
        electr_pwr_unit = 'kW'
    )

    add_generic_attributes(
        db_access,
        appliance_id,
        { 'q_kvar': q_kvar }
    )

    write_terminal_element_to_db(
        db_access,
        name,
        'load',
        bus,
        spatial_reference_id,
        network_id,
        network_graph_id,
        appliance_id
    )
