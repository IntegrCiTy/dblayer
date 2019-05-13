#!/usr/bin/env python
# coding: utf-8

from .sim_model_db_reader_base import *


class GasSimModelDBReader( SimModelDBReaderBase ):
    """
    Base class for constructing a simulation model for a gas network from information contained in the 3DCityDB.
    """

    def __init__( self, connect, verbose=False ):
        """
        Constructor.

        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        :param verbose: turn verbosity on/off (bool, optional, default=False)
        """

        super().__init__( connect )
        self.verbose = verbose


    @abc.abstractmethod
    def add_network_node(
        self, net, name, level, geodata
        ):
        """
        Add a junction for two or more pipes to the simulation model.

        :param net: simulation model
        :param name: name of the junction (string)
        :param level: pressure level (string)
        :param deodata: position of the junction (dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_feeder(
        self, net, name, node_id, p_lim_kw, p_pa, geodata
        ):
        """
        Add a feeder to the simulation model.

        :param net: simulation model
        :param name: name of the feeder (string)
        :param node_id: ID of connected network node (int)
        :param p_lim_kw: maximum power in kW flowing through the feeder (float)
        :param p_pa: operating pressure level in Pa at the output of the feeder (float)
        :param deodata: position of thermal sink (dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_sink(
        self, net, name, node_id, p_kw, geodata
        ):
        """
        Add a thermal sink to the simulation model.

        :param net: simulation model
        :param name: name of the electrical bus (string)
        :param node_id: ID of connected network node (int)
        :param p_kw: gas consumption in kW (float)
        :param deodata: position of thermal sink (dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_station(
        self, net, name, hp_node_id, lp_node_id, p_lim_kw, p_pa
        ):
        """
        Add a transformer to the simulation model.

        :param net: simulation model
        :param name: name of the transformer (string)
        :param hp_node_id: ID of connected high pressure network node (int)
        :param lp_node_id: ID of connected low pressure network node (int)
        :param p_lim_kw: maximum power in kW flowing through the station (float)
        :param p_pa: operating pressure level in Pa at the output of the station (float)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_pipe(
        self, net, name, from_node_id, to_node_id, diameter_m, length_m, geodata
        ):
        """
        Add a pipe to the simulation model.

        :param net: simulation model
        :param name: name of the pipe (string)
        :param from_node_id: ID of connected thermal node (int)
        :param to_node_id: ID of connected thermal node (int)
        :param diameter_m: diameter of the pipe in m (float)
        :param length_km: length of the pipe in km (float)
        :param geodata: position of the pipe (list of dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    def get_net( self, network_id ):
        """
        Retrieve the electrical network as pandapower model.
        """

        # Initialize dict: network feature ID --> network feature name
        self.feature_names = {}

        # Initialize dict: feature graph node ID --> feature graph ID
        self.feature_graph_ids = {}

        # Map structure from database to classes.
        self._map_classes()

        # Retrieve relevant data.
        self._retrieve_data_network_features( network_id )
        self._retrieve_data_feature_graphs( network_id )
        self._retrieve_data_generic_attributes( network_id )

        # Create empty network model.
        net = self.create_empty_network()

        # Add elements to network model.
        self._add_network_nodes( net )
        self._add_feeders( net )
        self._add_sinks( net )
        self._add_stations( net )
        self._add_pipes( net )

        return net


    def _map_classes( self ):
        """
        Map relevant structures from database to classes.
        """

        self.ComplexFunctionalElement = self.map_citydb_object_class(
            'ComplexFunctionalElement',
            table_name='utn9_ntw_feat_complex_funct_elem',
            schema='citydb_view'
            )

        self.RoundPipe = self.map_citydb_object_class(
            'RoundPipe',
            table_name='utn9_ntw_feat_distrib_elem_pipe_round',
            schema='citydb_view'
            )

        self.OtherShapePipe = self.map_citydb_object_class(
            'OtherShapePipe',
            table_name='utn9_ntw_feat_distrib_elem_pipe_other_shape',
            schema='citydb_view'
            )

        self.TerminalElement = self.map_citydb_object_class(
            'TerminalElement',
            table_name='utn9_ntw_feat_term_elem',
            schema='citydb_view'
            )

        self.NetworkGraph = self.map_citydb_object_class(
            'NetworkGraph',
            table_name='utn9_network_graph',
            schema='citydb_view'
            )

        self.FeatureGraph = self.map_citydb_object_class(
            'FeatureGraph'
            )

        self.Node = self.map_citydb_object_class(
            'Node',
            table_name='utn9_node',
            schema='citydb_view'
            )

        self.InterFeatureLink = self.map_citydb_object_class(
            'InterFeatureLink',
            table_name='utn9_link_interfeature',
            schema='citydb_view'
            )

        self.GenericAttribute = self.map_citydb_object_class(
           'GenericAttribute',
           table_name='cityobject_genericattrib_real',
           schema='citydb_view'
           )

        self.NetworkToFeature = self.map_citydb_object_class(
            'NetworkToFeature',
            table_name='utn9_network_to_network_feature',
            schema='citydb',
            user_defined = True
            )


    def _retrieve_data_network_features( self, network_id ):
        """
        After mapping the classes, retrieve all relevant data associated to network features.
        """

        self.feeders = self.join_citydb_objects(
            [ 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.TerminalElement, 'class' ) == 'gas-network-feeder',
                self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.sinks = self.join_citydb_objects(
            [ 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.TerminalElement, 'class' ) == 'gas-network-sink',
                self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.network_nodes = self.join_citydb_objects(
            [ 'OtherShapePipe', 'NetworkToFeature' ],
            conditions = [
                getattr( self.OtherShapePipe, 'class' ) == 'gas-network-node',
                self.OtherShapePipe.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.stations = self.join_citydb_objects(
            [ 'ComplexFunctionalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.ComplexFunctionalElement, 'class' ) == 'gas-network-station',
                self.ComplexFunctionalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.pipes = self.join_citydb_objects(
            [ 'RoundPipe', 'NetworkToFeature' ],
            conditions = [
                getattr( self.RoundPipe, 'class' ) == 'gas-network-pipe',
                self.RoundPipe.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )


    def _retrieve_data_feature_graphs( self, network_id ):
        """
        After mapping the classes, retrieve all relevant data associated to feature graphs.
        """

        self.feature_graphs = self.join_citydb_objects(
            [ 'FeatureGraph', 'NetworkToFeature' ],
            conditions = [
                self.FeatureGraph.ntw_feature_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.nodes = self.join_citydb_objects(
            [ 'Node', 'FeatureGraph', 'NetworkToFeature' ],
            conditions = [
                self.Node.feat_graph_id == self.FeatureGraph.id,
                self.FeatureGraph.ntw_feature_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.inter_feature_links = self.join_citydb_objects(
            [ 'InterFeatureLink', 'NetworkGraph' ],
            conditions = [
                self.InterFeatureLink.ntw_graph_id == self.NetworkGraph.id,
                self.NetworkGraph.network_id == network_id
                ],
            result_index = 0
            )


    def _retrieve_data_generic_attributes( self, network_id ):
        """
        After mapping the classes, retrieve all relevant data stored as generic attributes.
        """

        sink_attributes_consumption = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'gas_consumption',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        p_lim_kw_attributes = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'p_lim_kw',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        p_pa_attributes = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'p_pa',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        # Retrieve data associated to sinks stored as generic attributes.
        self.sink_consumption = {
            attr.cityobject_id: attr.realval for attr in sink_attributes_consumption
            }

        # Retrieve data associated to feeders and stations stored as generic attributes.
        self.p_lim_kw = {
            attr.cityobject_id: attr.realval for attr in p_lim_kw_attributes
            }
        self.p_pa = {
            attr.cityobject_id: attr.realval for attr in p_pa_attributes
            }


    def _add_network_nodes( self, net ):
        """
        Add network nodes to network.
        """

        ( self.ntwn_ids_and_names, ntwn_feature_graph_ids, self.ntwn_node_ids ) = \
            self._retrieve_feature_data( self.network_nodes, self.feature_graphs, self.nodes )

        self.ntwn_levels = {}

        for ntwn in self.network_nodes:

            self.ntwn_levels[ntwn.id] = ntwn.function_of_line

            ntwn_geom_wkt = self.execute_function( geom_as_text( ntwn.geom ) )
            ( x, y,z ) = from_wkt( ntwn_geom_wkt ).coords[0]

            self.add_network_node(
                net = net,
                name = ntwn.name,
                level = ntwn.function_of_line,
                geodata = self.geom_to_point2d( ntwn.geom )
                )


    def _add_feeders( self, net ):
        """
        Add feeders to network.
        """

        ( feeder_ids, feeder_feature_graph_ids, feeder_node_ids ) = \
            self._retrieve_feature_data( self.feeders, self.feature_graphs, self.nodes )

        all_node_feeder_connections = \
            self._retrieve_unique_connections( self.ntwn_node_ids, feeder_node_ids, self.inter_feature_links )

        for feeder in self.feeders:
            connected_node_id = all_node_feeder_connections[feeder.id]

            self.add_feeder(
                net = net,
                name = feeder.name,
                node_id = connected_node_id,
                p_lim_kw = float( self.p_lim_kw[feeder.id] ),
                p_pa = float( self.p_pa[feeder.id] ),
                geodata = self.geom_to_point2d( feeder.geom )
                )


    def _add_sinks( self, net ):
        """
        Add gas sinks to network.
        """

        ( sink_ids, sink_feature_graph_ids, sink_node_ids ) = \
            self._retrieve_feature_data( self.sinks, self.feature_graphs, self.nodes )

        all_node_sink_connections = \
            self._retrieve_unique_connections( self.ntwn_node_ids, sink_node_ids, self.inter_feature_links )

        for sink in self.sinks:
            connected_node_id = all_node_sink_connections[sink.id]

            self.add_sink(
                net = net,
                name = sink.name,
                node_id = connected_node_id,
                p_kw = float( self.sink_consumption[sink.id] ),
                geodata = self.geom_to_point2d( sink.geom )
                )


    def _add_stations( self, net ):
        """
        Add network stations to network.
        """

        ( station_ids, station_feature_graph_ids, station_node_ids ) = \
            self._retrieve_feature_data( self.stations, self.feature_graphs, self.nodes )

        all_node_station_connections = \
            self._retrieve_connections( self.ntwn_node_ids, station_node_ids, self.inter_feature_links )

        for station in self.stations:
            connected_node_ids = all_node_station_connections[station.id]

            if not len( connected_node_ids ) == 2:
                raise RuntimeError(
                    'station \'{}\' is not connected to 2 network nodes'.format( station.name )
                    )

            connected_node_levels = [
                self.ntwn_levels[id] for id in connected_node_ids
                ]

            if connected_node_levels[0] == 'MP' and connected_node_levels[1] == 'BP':
                hp_node_id = connected_node_ids[0]
                lp_node_id = connected_node_ids[1]
            elif connected_node_levels[0] == 'BP' and connected_node_levels[1] == 'MP':
                hp_node_id = connected_node_ids[1]
                lp_node_id = connected_node_ids[0]
            else:
                raise RuntimeError(
                    'station \'{}\' is not connected to 1 MP node and 1 BP node'.format( station.name )
                    )

            self.add_station(
                net = net,
                name = station.name,
                hp_node_id = hp_node_id,
                lp_node_id = lp_node_id,
                p_lim_kw = float( self.p_lim_kw[station.id] ),
                p_pa = float( self.p_pa[station.id] )
                )


    def _add_pipes( self, net ):
        """
        Add pipes to network.
        """

        ( pipe_ids, pipe_feature_graph_ids, pipe_node_ids ) = \
            self._retrieve_feature_data( self.pipes, self.feature_graphs, self.nodes )

        all_node_pipe_connections = self._retrieve_connections_with_link_control(
            self.ntwn_node_ids, pipe_node_ids, self.inter_feature_links
            )

        for pipe in self.pipes:
            connected_node_ids = all_node_pipe_connections[pipe.id]

            if not len( connected_node_ids ) == 2:
                raise RuntimeError(
                    'pipe \'{}\' is not connected to 2 thermal nodes'.format( pipe.name )
                    )

            if not connected_node_ids[0][1] == 'start' and connected_node_ids[1][1] == 'end' and \
               not connected_node_ids[0][1] == 'end' and connected_node_ids[1][1] == 'start':
                raise RuntimeError(
                    'inconsistent link control for pipe \'{}\''.format( pipe.name )
                    )

            if connected_node_ids[0][1] == 'start':
                from_node_id = connected_node_ids[0][0]
                to_node_id = connected_node_ids[1][0]
            else:
                from_node_id = connected_node_ids[1][0]
                to_node_id = connected_node_ids[0][0]

            length = self.execute_function( length_from_geom( pipe.geom ) )

            self.add_pipe(
                net = net,
                name = pipe.name,
                from_node_id = from_node_id,
                to_node_id = to_node_id,
                diameter_m = float( pipe.int_diameter ),
                length_m = length,
                geodata = self.geom_to_list_point2d( pipe.geom )
                )
