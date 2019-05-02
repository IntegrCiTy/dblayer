#!/usr/bin/env python
# coding: utf-8

import abc

from dblayer import *
from dblayer.func.func_postgis_geom import *
from sqlalchemy import or_

from pygeoif import from_wkt


class ElectricalSimModelDBReader( DBAccess, abc.ABC ):
    """
    Construct a simulation model for an electrical entwork from information contained in the 3DCityDB.
    """

    @abc.abstractmethod
    def create_empty_network( self ):
        """
        Create an empty network model.

        :return: empty network model
        """
        pass


    @abc.abstractmethod
    def add_bus(
            self, net, name, type, vn_kv, geodata
            ):
        """
        Add an electrical bus to the simulation model.

        :param name: name of the electrical bus (string)
        :param type: type of electrical bus (string)
        :param vn_kv: grid voltage level in kV (float)
        :param deodata: position of electrical bus (dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_line(
            self, net, name, from_bus_id, to_bus_id, type,
            c_nf_per_km, r_ohm_per_km, x_ohm_per_km, max_i_ka,
            length_km, geodata
            ):
        """
        Add an electrical line to the simulation model.

        :param name: name of the electrical line (string)
        :param from_bus_id: ID of connected bus (int)
        :param to_bus_id: ID of connected bus (int)
        :param type: type of line (string)
        :param c_nf_per_km: line capacitance in nF per km (float)
        :param r_ohm_per_km: line resistance in Ohm per km (float)
        :param x_ohm_per_km: line reactance in Ohm per km (float)
        :param max_i_ka: maximum thermal current in kA (float)
        :param length_km: length of the line in km (float)
        :param geodata: position of the line (list of dblayer.func.func_postgis_geom.Point2D)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_load(
            self, net, name, bus_id, p_kw, q_kvar
            ):
        """
        Add an electrical load to the simulation model.

        :param name: name of the electrical load (string)
        :param bus_id: ID of connected bus (int)
        :param p_kw: active power in kV (float)
        :param q_kvar: reactive power in kvar (float)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_transformer(
            self, net, name, hv_bus_id, lv_bus_id, type
            ):
        """
        Add a transformer to the simulation model.

        :param name: name of the transformer (string)
        :param hv_bus_id: ID of connected high-voltage bus (int)
        :param lv_bus_id: ID of connected low-voltage bus (int)
        :param type: type of transformer (string)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_switch(
            self, net, name, from_bus_id, to_bus_id, type
            ):
        """
        Add a switch to the simulation model.

        :param name: name of the switch (string)
        :param from_bus_id: ID of connected bus (int)
        :param to_bus_id: ID of connected bus (int)
        :param type: type of switch (string)

        :return: None
        """
        pass


    @abc.abstractmethod
    def add_ext_grid(
            self, net, name, bus_id
            ):
        """
        Add an external grid to the simulation model.

        :param name: name of the external grid (string)
        :param bus_id: ID of the connected bus (int)

        :return: None
        """
        pass


    def __init__( self, connect ):
        """
        Constructor.

        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        """

        super().__init__()
        self.connect_to_citydb( connect )


    def get_net( self, network_id ):
        """
        Retrieve the electrical network as pandapower model.
        """

        # Map structure from database to classes.
        self._map_classes()

        # Retrieve relevant data.
        self._retrieve_data_network_features( network_id )
        self._retrieve_data_feature_graphs( network_id )
        self._retrieve_data_generic_attributes( network_id )

        # From a topological point of view, the busses are the most important
        # features of the network to which everything is connected. For this
        # reason, additional bus data has to be extracted and stored.
        self._extract_bus_topological_data()

        # Create empty network model.
        net = self.create_empty_network()

        # Add elements to network model.
        self._add_busses( net )
        self._add_lines( net )
        self._add_loads( net )
        self._add_transformers( net )
        self._add_switches( net )
        self._add_external_grid( net )

        return net


    def _map_classes( self ):
        """
        Map relevant structures from database to classes.
        """

        self.SimpleFunctionalElement = self.map_citydb_object_class(
            'SimpleFunctionalElement',
            table_name='utn9_ntw_feat_simple_funct_elem',
            schema='citydb_view'
            )

        self.ComplexFunctionalElement = self.map_citydb_object_class(
            'ComplexFunctionalElement',
            table_name='utn9_ntw_feat_complex_funct_elem',
            schema='citydb_view'
            )

        self.TerminalElement = self.map_citydb_object_class(
            'TerminalElement',
            table_name='utn9_ntw_feat_term_elem',
            schema='citydb_view'
            )

        self.Cable = self.map_citydb_object_class(
            'Cable',
            table_name='utn9_ntw_feat_distrib_elem_cable',
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

        self.ElectricalAppliances = self.map_citydb_object_class(
            'ElectricalAppliances',
            table_name='nrg8_facilities_electrical_appliances',
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

        self.busses = self.join_citydb_objects(
            [ 'SimpleFunctionalElement', 'NetworkToFeature' ],
            conditions = [
                or_(
                    getattr( self.SimpleFunctionalElement, 'class' ) == 'busbar',
                    getattr( self.SimpleFunctionalElement, 'class' ) == 'plate',
                    getattr( self.SimpleFunctionalElement, 'class' ) == 'supply point',
                    getattr( self.SimpleFunctionalElement, 'class' ) == 'pole'
                    ),
                self.SimpleFunctionalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.lines = self.join_citydb_objects(
            [ 'Cable', 'NetworkToFeature' ],
            conditions = [
                self.Cable.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.loads = self.join_citydb_objects(
            [ 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.TerminalElement, 'class' ) == 'load',
                self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.trafos = self.join_citydb_objects(
            [ 'ComplexFunctionalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.ComplexFunctionalElement, 'class' ) == 'transformer',
                self.ComplexFunctionalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.switches = self.join_citydb_objects(
            [ 'SimpleFunctionalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.SimpleFunctionalElement, 'class' ) == 'switch',
                self.SimpleFunctionalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.external_grids = self.join_citydb_objects(
            [ 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                getattr( self.TerminalElement, 'class' ) == 'external-grid',
                self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        self.electrical_appliances = self.join_citydb_objects(
            [ 'ElectricalAppliances', 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                self.ElectricalAppliances.id == self.TerminalElement.cityobject_id,
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

        # Map feature graph IDs to their associated network feature IDs.
        self.feature_ids = { feature_graph.id: feature_graph.ntw_feature_id  for feature_graph in self.feature_graphs }

        # Map feature graph node IDs to the name of the feature graph node.
        self.node_names = { node.id : node.name for node in self.nodes }


    def _retrieve_data_generic_attributes( self, network_id ):
        """
        After mapping the classes, retrieve all relevant data stored as generic attributes.
        """

        bus_attributes = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'vn_kv',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        line_attributes_c_nf_per_km = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'c_nf_per_km',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        line_attributes_r_ohm_per_km = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'r_ohm_per_km',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        line_attributes_x_ohm_per_km = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'x_ohm_per_km',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        line_attributes_max_i_ka = self.join_citydb_objects(
            [ 'GenericAttribute', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'max_i_ka',
                self.GenericAttribute.cityobject_id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        load_attributes = self.join_citydb_objects(
            [ 'GenericAttribute', 'TerminalElement', 'NetworkToFeature' ],
            conditions = [
                self.GenericAttribute.attrname == 'q_kvar',
                self.GenericAttribute.cityobject_id == self.TerminalElement.cityobject_id,self.TerminalElement.id == self.NetworkToFeature.network_feature_id,
                self.NetworkToFeature.network_id == network_id
                ],
            result_index = 0
            )

        # Retrieve data associated to busses stored as generic attributes.
        self.bus_vn_kv = {
            attr.cityobject_id: attr.realval for attr in bus_attributes
            }

        # Retrieve data associated to lines stored as generic attributes.
        self.line_c_nf_per_km = {
            attr.cityobject_id: attr.realval for attr in line_attributes_c_nf_per_km
            }
        self.line_r_ohm_per_km = {
            attr.cityobject_id: attr.realval for attr in line_attributes_r_ohm_per_km
            }
        self.line_x_ohm_per_km = {
            attr.cityobject_id: attr.realval for attr in line_attributes_x_ohm_per_km
            }
        self.line_max_i_ka = {
            attr.cityobject_id: attr.realval for attr in line_attributes_max_i_ka
            }

        # Retrieve data associated to loads stored as generic attributes.
        self.load_q_kvar = {
            attr.cityobject_id: attr.realval for attr in load_attributes
            }


    def _extract_bus_topological_data( self ):
        """
        From a topological point of view, the busses are the most important features of the network to which everything is connected. For this reason, additional bus data has to be extracted and stored.
        """

        # Create dict of IDs and names for all busses.
        self.bus_ids_and_names = { bus.id: bus.name for bus in self.busses }

        # Create dict of IDs of busses and associated feature graphs.
        self.bus_feature_graph_ids = {
            feature_graph.id: feature_graph.ntw_feature_id
            for feature_graph in self.feature_graphs
            if feature_graph.ntw_feature_id in self.bus_ids_and_names }

        # Create dict of IDs of nodes and feature graphs associated with busses.
        self.bus_node_ids = {
            node.id : self.bus_feature_graph_ids[node.feat_graph_id]
            for node in self.nodes
            if node.feat_graph_id in self.bus_feature_graph_ids
            }


    def _add_busses( self, net ):
        """
        Add busses to network.
        """

        for bus in self.busses:
            bus_geom_wkt = self.execute_function( geom_as_text( bus.geom ) )
            ( x, y,z ) = from_wkt( bus_geom_wkt ).coords[0]

            bus_type = 'b' if getattr( bus, 'class' ) == 'busbar' else 'n'

            self.add_bus(
                net = net,
                name = bus.name,
                type = bus_type,
                vn_kv = self.bus_vn_kv[bus.id],
                geodata = Point2D( x, y )
                )


    def _add_lines( self, net ):
        """
        Add lines to network.
        """

        line_ids = [ line.id for line in self.lines ]

        line_feature_graph_ids = {
            feature_graph.id: feature_graph.ntw_feature_id
            for feature_graph in self.feature_graphs
            if feature_graph.ntw_feature_id in line_ids
            }

        line_node_ids = {
            node.id : line_feature_graph_ids[node.feat_graph_id]
            for node in self.nodes
            if node.feat_graph_id in line_feature_graph_ids
            }

        bus_to_line_connections = [
            ( line_node_ids[link.end_node_id], self.bus_node_ids[link.start_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in self.bus_node_ids
            and link.end_node_id in line_node_ids
            ]

        line_to_bus_connections = [
            ( line_node_ids[link.start_node_id], self.bus_node_ids[link.end_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in line_node_ids
            and link.end_node_id in self.bus_node_ids
            ]

        all_bus_line_connections = {}

        for connection in ( bus_to_line_connections + line_to_bus_connections ):
            line_id = connection[0]
            bus_id = connection[1]
            if not line_id in all_bus_line_connections:
                all_bus_line_connections[line_id] = [bus_id]
            else:
                all_bus_line_connections[line_id].append(bus_id)

        for line in self.lines:
            connected_bus_ids = all_bus_line_connections[line.id]

            if not len( connected_bus_ids ) == 2:
                    raise RuntimeError(
                        'line \'{}\' is not connected to 2 busses'.format( line.name )
                        )

            length = 1e-3 * self.execute_function( length_from_geom( line.geom ) )

            line_geom_wkt = self.execute_function( geom_as_text( line.geom ) )
            line_coords = from_wkt( line_geom_wkt ).coords
            line_geomdata = [ Point2D( c[0], c[1] ) for c in line_coords ]

            self.add_line(
                net = net,
                name = line.name,
                from_bus_id = connected_bus_ids[0],
                to_bus_id = connected_bus_ids[1],
                type = line.function,
                c_nf_per_km = self.line_c_nf_per_km[line.id],
                r_ohm_per_km = self.line_r_ohm_per_km[line.id],
                x_ohm_per_km = self.line_x_ohm_per_km[line.id],
                max_i_ka = self.line_max_i_ka[line.id],
                length_km = length,
                geodata = line_geomdata
                )


    def _add_loads( self, net ):
        """
        Add loads to network.
        """

        load_ids = [ load.id for load in self.loads ]

        elec_appliance_ids = {
            appliance.id: appliance
            for appliance in self.electrical_appliances
            }

        load_feature_graph_ids = {
            feature_graph.id: feature_graph.ntw_feature_id
            for feature_graph in self.feature_graphs
            if feature_graph.ntw_feature_id in load_ids
            }

        load_node_ids = {
            node.id : load_feature_graph_ids[node.feat_graph_id]
            for node in self.nodes
            if node.feat_graph_id in load_feature_graph_ids
            }

        bus_to_load_connections = [
            ( load_node_ids[link.end_node_id], self.bus_node_ids[link.start_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in self.bus_node_ids
            and link.end_node_id in load_node_ids
            ]

        load_to_bus_connections = [
            ( load_node_ids[link.start_node_id], self.bus_node_ids[link.end_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in load_node_ids
            and link.end_node_id in self.bus_node_ids
            ]

        all_bus_load_connections = {}

        for connection in ( bus_to_load_connections + load_to_bus_connections ):
            load_id = connection[0]
            bus_id = connection[1]
            if not load_id in all_bus_load_connections:
                all_bus_load_connections[load_id] = bus_id
            else:
                raise RuntimeError(
                    'load with ID {} is connected to more than 1 bus'.format( load_id )
                    )

        for load in self.loads:
            connected_bus_id = all_bus_load_connections[load.id]
            connected_electrical_appliance = elec_appliance_ids[load.cityobject_id]

            self.add_load(
                net = net,
                name = load.name,
                bus_id = connected_bus_id,
                p_kw = connected_electrical_appliance.electr_pwr,
                q_kvar = self.load_q_kvar[connected_electrical_appliance.id]
                )


    def _add_transformers( self, net ):
        """
        Add transfomers to network.
        """

        trafo_ids = [ trafo.id for trafo in self.trafos ]

        trafo_feature_graph_ids = {
            feature_graph.id: feature_graph.ntw_feature_id
            for feature_graph in self.feature_graphs
            if feature_graph.ntw_feature_id in trafo_ids
            }

        trafo_node_ids = {
            node.id : trafo_feature_graph_ids[node.feat_graph_id]
            for node in self.nodes
            if node.feat_graph_id in trafo_feature_graph_ids
            }

        bus_to_trafo_connections = [
            ( trafo_node_ids[link.end_node_id], self.bus_node_ids[link.start_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in self.bus_node_ids
            and link.end_node_id in trafo_node_ids
            ]

        trafo_to_bus_connections = [
            ( trafo_node_ids[link.start_node_id], self.bus_node_ids[link.end_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in trafo_node_ids
            and link.end_node_id in self.bus_node_ids
            ]

        all_bus_trafo_connections = {}

        for connection in ( bus_to_trafo_connections + trafo_to_bus_connections ):
            trafo_id = connection[0]
            bus_id = connection[1]
            if not trafo_id in all_bus_trafo_connections:
                all_bus_trafo_connections[trafo_id] = [bus_id]
            else:
                all_bus_trafo_connections[trafo_id].append(bus_id)

        for trafo in self.trafos:
            connected_bus_ids = all_bus_trafo_connections[trafo.id]

            if not len( connected_bus_ids ) == 2:
                raise RuntimeError(
                    'trafo \'{}\' is not connected to 2 busses'.format( trafo.name )
                    )

            connected_bus_names = [
                self.bus_ids_and_names[id] for id in connected_bus_ids
                ]

            if '-LV' in connected_bus_names[0].upper() and '-MV' in connected_bus_names[1].upper():
                lv_bus_id = connected_bus_ids[0]
                hv_bus_id = connected_bus_ids[1]
            elif '-MV' in connected_bus_names[0].upper() and '-LV' in connected_bus_names[1].upper():
                lv_bus_id = connected_bus_ids[1]
                hv_bus_id = connected_bus_ids[0]
            else:
                raise RuntimeError(
                    'trafo \'{}\' is not connected to 1 LV bus and 1 MV bus'.format( trafo.name )
                    )

            self.add_transformer(
                net = net,
                name = trafo.name,
                hv_bus_id = hv_bus_id,
                lv_bus_id = lv_bus_id,
                type = trafo.function
                )


    def _add_switches( self, net ):
        """
        Add switches to network.
        """

        switch_ids = [ switch.id for switch in self.switches ]

        switch_feature_graph_ids = {
            feature_graph.id: feature_graph.ntw_feature_id
            for feature_graph in self.feature_graphs
            if feature_graph.ntw_feature_id in switch_ids
            }

        switch_node_ids = {
            node.id : switch_feature_graph_ids[node.feat_graph_id]
            for node in self.nodes
            if node.feat_graph_id in switch_feature_graph_ids
            }

        bus_to_switch_connections = [
            ( switch_node_ids[link.end_node_id], self.bus_node_ids[link.start_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in self.bus_node_ids
            and link.end_node_id in switch_node_ids
            ]

        switch_to_bus_connections = [
            ( switch_node_ids[link.start_node_id], self.bus_node_ids[link.end_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in switch_node_ids
            and link.end_node_id in self.bus_node_ids
            ]

        all_bus_switch_connections = {}

        for connection in ( bus_to_switch_connections + switch_to_bus_connections ):
            switch_id = connection[0]
            bus_id = connection[1]
            if not switch_id in all_bus_switch_connections:
                all_bus_switch_connections[switch_id] = [bus_id]
            else:
                all_bus_switch_connections[switch_id].append(bus_id)


        for switch in self.switches:
            connected_bus_ids = all_bus_switch_connections[switch.id]

            if not len( connected_bus_ids ) == 2:
                    raise RuntimeError(
                        'switch \'{}\' is not connected to 2 busses'.format( switch.name )
                        )

            from_bus_id = connected_bus_ids[0]
            to_bus_id = connected_bus_ids[1]

            self.add_switch(
                net = net,
                name = switch.name,
                from_bus_id = from_bus_id,
                to_bus_id = to_bus_id,
                type = switch.function
                )


    def _add_external_grid( self, net ):
        """
        Add an external grid to the network.
        """

        ext_grid_ids = [ ext_grid.id for ext_grid in self.external_grids ]

        ext_grid_feature_graph_ids = {
            feature_graph.id: feature_graph.ntw_feature_id
            for feature_graph in self.feature_graphs
            if feature_graph.ntw_feature_id in ext_grid_ids
            }

        ext_grid_node_ids = {
            node.id : ext_grid_feature_graph_ids[node.feat_graph_id]
            for node in self.nodes
            if node.feat_graph_id in ext_grid_feature_graph_ids
            }

        bus_to_ext_grid_connections = [
            ( ext_grid_node_ids[link.end_node_id], self.bus_node_ids[link.start_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in self.bus_node_ids
            and link.end_node_id in ext_grid_node_ids
            ]

        ext_grid_to_bus_connections = [
            ( ext_grid_node_ids[link.start_node_id], self.bus_node_ids[link.end_node_id] )
            for link in self.inter_feature_links
            if link.start_node_id in ext_grid_node_ids
            and link.end_node_id in self.bus_node_ids
            ]

        all_bus_ext_grid_connections = {}

        for connection in ( bus_to_ext_grid_connections + ext_grid_to_bus_connections ):

            ext_grid_id = connection[0]
            bus_id = connection[1]
            if not ext_grid_id in all_bus_ext_grid_connections:
                all_bus_ext_grid_connections[ext_grid_id] = bus_id
            else:
                raise RuntimeError(
                    'external grid with ID {} is connected to more than 1 bus'.format( ext_grid_id )
                    )

        for ext_grid in self.external_grids:

            connected_bus_id = all_bus_ext_grid_connections[ext_grid.id]
            self.add_ext_grid(
                net = net,
                name = ext_grid.name,
                bus_id = connected_bus_id
                )
