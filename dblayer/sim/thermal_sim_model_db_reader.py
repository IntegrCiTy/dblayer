#!/usr/bin/env python
# coding: utf-8

from .sim_model_db_reader_base import *


class ThermalSimModelDBReader( SimModelDBReaderBase ):
    """
    Base class for constructing a simulation model for a thermal network from information contained in the 3DCityDB.
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
    def add_thermal_source(
        self, net, name, geodata
        ):
        """
        Add a thermal source to the simulation model.

        :param net: simulation model
        :param name: name of the thermal source (string)
        :param deodata: position of thermal sink (dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_sink(
        self, net, name, heat_diss_kw, geodata
        ):
        """
        Add a thermal sink to the simulation model.

        :param net: simulation model
        :param name: name of the electrical bus (string)
        :param heat_diss_kw: total heat dissipation in kW (float)
        :param deodata: position of thermal sink (dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_junction(
        self, net, name, geodata
        ):
        """
        Add a junction for two or more pipes to the simulation model.

        :param net: simulation model
        :param name: name of the junction (string)
        :param deodata: position of the junction (dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_pipe(
        self, net, name, from_node_id, to_node_id, length_km, geodata
        ):
        """
        Add a pipe to the simulation model.

        :param net: simulation model
        :param name: name of the pipe (string)
        :param from_node_id: ID of connected thermal node (int)
        :param to_node_id: ID of connected thermal node (int)
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
        self._add_thermal_sources( net )
        self._add_sinks( net )
        self._add_junctions( net )
        self._add_pipes( net )

        return net


    def _map_classes( self ):
        """
        Map relevant structures from database to classes.
        """

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

        self.DHWFacilities = self.map_citydb_object_class(
            'DHWFacilities',
            table_name='nrg8_facilities_dhw',
            schema='citydb_view'
            )

        #self.GenericAttribute = self.map_citydb_object_class(
        #    'GenericAttribute',
        #    table_name='cityobject_genericattrib_real',
        #    schema='citydb_view'
        #    )

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

        self.sources = self.join_citydb_objects(
            [ 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.TerminalElement, 'class' ) == 'thermal-source',
                self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.sinks = self.join_citydb_objects(
            [ 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.TerminalElement, 'class' ) == 'thermal-sink',
                self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.junctions = self.join_citydb_objects(
            [ 'OtherShapePipe', 'NetworkToFeature' ],
            conditions = [
                self.OtherShapePipe.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.pipes = self.join_citydb_objects(
            [ 'RoundPipe', 'NetworkToFeature' ],
            conditions = [
                self.RoundPipe.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.dhw_facilities = self.join_citydb_objects(
            [ 'DHWFacilities', 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                self.DHWFacilities.id == self.TerminalElement.cityobject_id,
                self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
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

        pass


    def _add_thermal_sources( self, net ):
        """
        Add thermal sources to network.
        """

        ( src_ids, src_feature_graph_ids, src_node_ids ) = \
            self._retrieve_feature_data( self.sources, self.feature_graphs, self.nodes )

        # Add thermal sources to dicts.
        self.feature_names.update( src_ids )
        self.feature_graph_ids.update( src_node_ids )

        for src in self.sources:

            self.add_thermal_source(
                net = net,
                name = src.name,
                geodata = self.geom_to_point2d( src.geom )
                )


    def _add_sinks( self, net ):
        """
        Add thermal sinks to network.
        """

        dhw_facility_ids = {
            dhw_facility.id: dhw_facility
            for dhw_facility in self.dhw_facilities
            }

        ( sink_ids, sink_feature_graph_ids, sink_node_ids ) = \
            self._retrieve_feature_data( self.sinks, self.feature_graphs, self.nodes )

        # Add thermal sinks to dicts.
        self.feature_names.update( sink_ids )
        self.feature_graph_ids.update( sink_node_ids )

        for sink in self.sinks:

            dhw_facility = dhw_facility_ids[sink.cityobject_id]

            self.add_sink(
                net = net,
                name = sink.name,
                heat_diss_kw = float( dhw_facility.heat_diss_tot_value ),
                geodata = self.geom_to_point2d( sink.geom )
                )


    def _add_junctions( self, net ):
        """
        Add pipe junctions to network.
        """

        ( junction_ids, junction_feature_graph_ids, junction_node_ids ) = \
            self._retrieve_feature_data( self.junctions, self.feature_graphs, self.nodes )

        # Add pipe junctions to dicts.
        self.feature_names.update( junction_ids )
        self.feature_graph_ids.update( junction_node_ids )

        for junction in self.junctions:

            self.add_junction(
                net = net,
                name = junction.name,
                geodata = self.geom_to_point2d( junction.geom )
                )


    def _add_pipes( self, net ):
        """
        Add pipes to network.
        """

        ( pipe_ids, pipe_feature_graph_ids, pipe_node_ids ) = \
            self._retrieve_feature_data( self.pipes, self.feature_graphs, self.nodes )

        all_node_pipe_connections = \
            self._retrieve_connections_with_link_control(
                self.feature_graph_ids, pipe_node_ids, self.inter_feature_links
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

            length = 1e-3 * self.execute_function( length_from_geom( pipe.geom ) )

            pipe_geomdata = self.geom_to_list_point2d( pipe.geom )

            self.add_pipe(
                net = net,
                name = pipe.name,
                from_node_id = from_node_id,
                to_node_id = to_node_id,
                length_km = length,
                geodata = pipe_geomdata
                )
