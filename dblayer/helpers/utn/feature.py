from dblayer import *
from dblayer.func.func_citydb_view_utn import *
from dblayer.func.func_postgis_geom import *



def insert_ntw_feature_2dpoint(
    access,
    insert_ntw_feature_func,
    srid,
    network_id,
    network_graph_id,
    feature_name,
    position,
    **feature_attrs ):
    '''
    Add a new newtwork feature, represented by a 2D point.
    In addition to the new network feature, a feature graph containing a single exterior node is created.

    :param access: instance of database interface (DBAccess)
    :param insert_ntw_feature_func: insert function for network feature (sqlalchemy.sql.functions.Function)
    :param srid: spatial reference ID (int)
    :param network_id: ID of network (int)
    :param network_graph_id: ID of network graph (int)
    :param feature_name: name of new feature (str)
    :param position: position of new feature (Point2D)
    :param feature_args: additional keyword arguments to be used by function insert_ntw_feature_func (**kwargs)
    :return: tuple containing the new feature ID, feature graph ID and node ID
    '''
    if not isinstance( access, DBAccess ):
        raise TypeError( 'parameter \'access\' must be of type \'DBAccess\'' )

    if not callable( insert_ntw_feature_func ):
        raise TypeError( 'parameter \'insert_ntw_feature_func\' must be a callable function' )

    if not isinstance( position, Point2D ):
        raise TypeError( 'parameter \'position\' must be of type \'Point2D\'' )

    # Insert new network feature (using the specific insert function).
    feature_id = access.add_citydb_object(
        insert_ntw_feature_func,
        name = feature_name,
        geom = access.execute_function(
            geom_from_2dpoint( position, srid )
        ),
        **feature_attrs
    )

    # Asscoiate new network feature with network.
    access.add_citydb_object(
        insert_network_to_network_feature,
        network_feature_id = feature_id,
        network_id = network_id
    )

    # Insert new feature graph.
    feature_graph_id = access.add_citydb_object(
        insert_feature_graph,
        name = 'feature_graph_' + feature_name,
        ntw_feature_id = feature_id,
        ntw_graph_id = network_graph_id
    )

    # Insert a single 2D point into the featur graph as exterior node.
    node_id = access.add_citydb_object(
        insert_node,
        name = 'node_' + feature_name,
        type = 'exterior',
        feat_graph_id = feature_graph_id,
        point_geom = access.execute_function(
            geom_from_2dpoint( position, srid )
        )
    )

    return feature_id, feature_graph_id, node_id



def insert_and_link_ntw_feature_2dpoint(
    access,
    insert_ntw_feature_func,
    srid,
    network_id,
    network_graph_id,
    feature_name,
    position,
    link_node_id,
    link_type = 'connects',
    **feature_attrs ):
    '''
    Add a new newtwork feature, represented by a 2D point.
    In addition to the new network feature, a feature graph containing a single exterior node is created.
    Furthermore, this new node is connected via an inter feature link to another exterior node.

    :param access: instance of database interface (DBAccess)
    :param insert_ntw_feature_func: insert function for network feature (sqlalchemy.sql.functions.Function)
    :param srid: spatial reference ID (int)
    :param network_id: ID of network (int)
    :param network_graph_id: ID of network graph (int)
    :param feature_name: name of new feature (str)
    :param position: position of new feature (Point2D)
    :param link_node_id: ID of the node that will be linked (int)
    :param link_type: type of link (str: contains/connects)
    :param feature_args: additional keyword arguments to be used by function insert_ntw_feature_func (**kwargs)
    :return: tuple containing the new feature ID, feature graph ID, node ID and inter feature link ID
    '''
    
    # Insert the new network feature.
    feature_id, feature_graph_id, node_id = insert_ntw_feature_2dpoint(
        access,
        insert_ntw_feature_func,
        srid,
        network_id,
        network_graph_id,
        feature_name,
        position,
        **feature_attrs
    )

    # Link the new network feature's only node to another existing node.
    inter_feature_link_id = access.add_citydb_object(
        insert_link_interfeature,
        name = 'inter_feature_link_' + feature_name,
        interfeature_link_type = link_type,
        start_node_id = node_id,
        end_node_id = link_node_id,
        ntw_graph_id = network_graph_id
    )

    return feature_id, feature_graph_id, node_id, inter_feature_link_id


def insert_ntw_feature_2dlinestring(
    access,
    insert_ntw_feature_func,
    srid,
    network_id,
    network_graph_id,
    feature_name,
    line_segment,
    **feature_attrs ):
    '''
    Add a new newtwork feature, represented by a 2D line (made up of 2D points).
    In addition to the new network feature, a feature graph containing a 2D line is created.
    The start and end points of this line are associated to exterior nodes and linked via an interior feature link.

    :param access: instance of database interface (DBAccess)
    :param insert_ntw_feature_func: insert function for network feature (sqlalchemy.sql.functions.Function)
    :param srid: spatial reference ID (int)
    :param network_id: ID of network (int)
    :param network_graph_id: ID of network graph (int)
    :param feature_name: name of new feature (str)
    :param line_segment: list of 2D points defining the 2D line segment (list of Point2D)
    :param feature_args: additional keyword arguments to be used by function insert_ntw_feature_func (**kwargs)
    :return: tuple containing the new feature ID, feature graph ID, the IDs of the start and end node and the interior feature link ID
    '''
    if not isinstance( access, DBAccess ):
        raise TypeError( 'parameter \'access\' must be of type \'DBAccess\'' )

    if not callable( insert_ntw_feature_func ):
        raise TypeError( 'parameter \'insert_ntw_feature_func\' must be a callable function' )

    if not all( isinstance( p, Point2D ) for p in line_segment ):
        raise TypeError( 'parameter \'line_segment\' must be of type \'list of Point2D\'' )

    # Insert new network feature (using the specific insert function).
    feature_id = access.add_citydb_object(
        insert_ntw_feature_func,
        name = feature_name,
        geom = access.execute_function(
            geom_from_2dlinestring( line_segment, srid )
        ),
        **feature_attrs
    )

    # Asscoiate new network feature with network.
    access.add_citydb_object(
        insert_network_to_network_feature,
        network_feature_id = feature_id,
        network_id = network_id
    )

    # Insert new feature graph.
    feature_graph_id = access.add_citydb_object(
        insert_feature_graph,
        name = 'feature_graph_' + feature_name,
        ntw_feature_id = feature_id,
        ntw_graph_id = network_graph_id
    )

    # Add the first point of the line segment as exterior node.
    start_node_id = access.add_citydb_object(
        insert_node,
        name = 'start_node_' + feature_name,
        type = 'exterior',
        feat_graph_id = feature_graph_id,
        point_geom = access.execute_function(
            geom_from_2dpoint( line_segment[0], srid )
        )
    )

    # Add the last point of the line segment as exterior node.
    end_node_id = access.add_citydb_object(
        insert_node,
        name = 'end_node_' + feature_name,
        type = 'exterior',
        feat_graph_id = feature_graph_id,
        point_geom = access.execute_function(
            geom_from_2dpoint( line_segment[-1], srid )
        )
    )

    # Link the two nodes with an interior feature link.
    interior_feature_link_id = access.add_citydb_object(
        insert_link_interior_feature,
        name = 'interior_feature_link_' + feature_name,
        start_node_id = start_node_id,
        end_node_id = end_node_id,
        feat_graph_id = feature_graph_id
    )

    return ( feature_id, feature_graph_id, start_node_id, end_node_id,
        interior_feature_link_id )


def insert_and_link_ntw_feature_2dlinestring(
    access,
    insert_ntw_feature_func,
    srid,
    network_id,
    network_graph_id,
    feature_name,
    line_segment,
    start_link_node_id,
    end_link_node_id,
    link_type = 'connects',
    **feature_attrs ):
    '''
    Add a new newtwork feature, represented by a 2D line segment (made up of 2D points).
    In addition to the new network feature, a feature graph containing a 2D line segment is created.
    The start and end points of this line segment are associated to exterior nodes and linked via an interior feature link.

    :param access: instance of database interface (DBAccess)
    :param insert_ntw_feature_func: insert function for network feature (sqlalchemy.sql.functions.Function)
    :param srid: spatial reference ID (int)
    :param network_id: ID of network (int)
    :param network_graph_id: ID of network graph (int)
    :param feature_name: name of new feature (str)
    :param line_segment: list of 2D points defining the 2D line segment (list of Point2D)
    :param start_link_node_id: ID of the node that will be linked to the first point of the line segment (int)
    :param end_link_node_id: ID of the node that will be linked to the last point of the line segment (int)
    :param link_type: type of link (str: contains/connects)
    :param feature_args: additional keyword arguments to be used by function insert_ntw_feature_func (**kwargs)
    :return: tuple containing the new feature ID, feature graph ID, the IDs of the start and end node, the inter feature link IDs and the interior feature link ID
    '''
    ( feature_id, feature_graph_id, start_node_id, end_node_id,
        interior_feature_link_id ) = insert_ntw_feature_2dlinestring(
        access,
        insert_ntw_feature_func,
        srid,
        network_id,
        network_graph_id,
        feature_name,
        line_segment,
        **feature_attrs
    )

    # Link the new network feature's first point of the line
    # segment to an already existing node.
    start_inter_feature_link_id = access.add_citydb_object(
        insert_link_interfeature,
        name = 'start_inter_feature_link_' + feature_name,
        interfeature_link_type = link_type,
        start_node_id = start_node_id,
        end_node_id = start_link_node_id,
        ntw_graph_id = network_graph_id
    )

    # Link the new network feature's least point of the line
    # segment to an already existing node.
    end_inter_feature_link_id = access.add_citydb_object(
        insert_link_interfeature,
        name = 'end_inter_feature_link_' + feature_name,
        interfeature_link_type = link_type,
        start_node_id = end_node_id,
        end_node_id = end_link_node_id,
        ntw_graph_id = network_graph_id
    )

    return ( feature_id, feature_graph_id, start_node_id, end_node_id,
        start_inter_feature_link_id, end_inter_feature_link_id,
        interior_feature_link_id )
