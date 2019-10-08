
import abc

from dblayer.access import *
from dblayer.func.func_postgis_geom import *

from pygeoif import from_wkt


class SimModelDBReaderBase( DBAccess, abc.ABC ):

    @abc.abstractmethod
    def create_empty_network( self ):
        """
        Create an empty network model.

        :return: empty network model
        """
        pass


    @abc.abstractmethod
    def get_net( self, network_id ):
        """
        Retrieve the simulation model for the network.
        """


    def __init__( self, connect ):
        """
        Constructor.

        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        """

        super().__init__()
        self.connect_to_citydb( connect )


    def geom_to_point2d( self, geom ):
        geom_wkt = self.execute_function( geom_as_text( geom ) )
        ( x, y,z ) = from_wkt( geom_wkt ).coords[0]
        return Point2D( x, y )


    def geom_to_list_point2d( self, geom ):
        geom_wkt = self.execute_function( geom_as_text( geom ) )
        coords = from_wkt( geom_wkt ).coords
        return [ Point2D( c[0], c[1] ) for c in coords ]


    def _retrieve_feature_data( self, features, feature_graphs, nodes ):

        # Create dict of IDs and names for these network features.
        ids = { f.id: f.name for f in features }

        # Create dict of IDs of network features and associated feature graphs.
        feature_graph_ids = {
            fg.id: fg.ntw_feature_id
            for fg in feature_graphs if fg.ntw_feature_id in ids
            }

        # Create dict of IDs of feature graph nodes and feature graphs associated with these netwrok features.
        node_ids = {
            n.id : feature_graph_ids[n.feat_graph_id]
            for n in nodes if n.feat_graph_id in feature_graph_ids
            }

        return ( ids, feature_graph_ids, node_ids )


    def _retrieve_connections( self, node_ids, edge_ids, links ):

        node_to_edge_connections = [
            ( edge_ids[l.end_node_id], node_ids[l.start_node_id] )
            for l in links if l.start_node_id in node_ids and l.end_node_id in edge_ids
            ]

        edge_to_node_connections = [
            ( edge_ids[l.start_node_id], node_ids[l.end_node_id] )
            for l in links if l.start_node_id in edge_ids and l.end_node_id in node_ids
            ]

        connections = {}

        for conn in ( node_to_edge_connections + edge_to_node_connections ):
            edge_id = conn[0]
            node_id = conn[1]
            if not edge_id in connections:
                connections[edge_id] = [ node_id ]
            else:
                connections[edge_id].append( node_id )

        return connections


    def _retrieve_unique_connections( self, node_ids, edge_ids, links ):

        node_to_edge_connections = [
            ( edge_ids[l.end_node_id], node_ids[l.start_node_id] )
            for l in links if l.start_node_id in node_ids and l.end_node_id in edge_ids
            ]

        edge_to_node_connections = [
            ( edge_ids[l.start_node_id], node_ids[l.end_node_id] )
            for l in links if l.start_node_id in edge_ids and l.end_node_id in node_ids
            ]

        connections = {}

        for conn in ( node_to_edge_connections + edge_to_node_connections ):
            edge_id = conn[0]
            node_id = conn[1]
            if not edge_id in connections:
                connections[edge_id] = node_id
            else:
                raise RuntimeError(
                    'network feature with ID {} is connected to more than 1 other network feature'.format( ext_grid_id )
                    )

        return connections
        
        
    def _retrieve_connections_with_link_control( self, node_ids, edge_ids, links ):

        node_to_edge_connections = [
            ( edge_ids[l.end_node_id], node_ids[l.start_node_id], l.link_control )
            for l in links if l.start_node_id in node_ids and l.end_node_id in edge_ids
            ]

        edge_to_node_connections = [
            ( edge_ids[l.start_node_id], node_ids[l.end_node_id], l.link_control )
            for l in links if l.start_node_id in edge_ids and l.end_node_id in node_ids
            ]

        connections = {}

        for conn in ( node_to_edge_connections + edge_to_node_connections ):
            edge_id = conn[0]
            node_id = conn[1]
            link_control = conn[2]
            if not edge_id in connections:
                connections[edge_id] = [ ( node_id, link_control ) ]
            else:
                connections[edge_id].append( ( node_id, link_control ) )

        return connections
