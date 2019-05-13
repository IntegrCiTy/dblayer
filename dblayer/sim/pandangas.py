#!/usr/bin/env python
# coding: utf-8

from .gas_sim_model_db_reader import GasSimModelDBReader

# Import pandangas module.
import pandangas as pg

import warnings


class PandaNGasModelDBReader( GasSimModelDBReader ):
    """
    Construct a pandngas simulation model from information contained in the 3DCityDB.
    """

    def create_empty_network( self ):
        """
        Create an empty network model.

        :return: empty network model (pandapower.auxiliary.pandapowerNet)
        """

        return pg.create_empty_network()


    def add_network_node(
        self, net, name, level, geodata
        ):

        pg.create_bus(
            net = net,
            name = name,
            level = level
            )
        #print( 'pg.create_bus( net, "{}", "{}" )'.format(name, level) )


    def add_feeder(
        self, net, name, node_id, p_lim_kw, p_pa, geodata
        ):

        pg.create_feeder(
            net = net,
            bus = self.ntwn_ids_and_names[node_id],
            p_lim_kW = p_lim_kw,
            p_Pa = p_pa,
            name = name
            )
        #print( 'pg.create_feeder( net, "{}", "{}", "{}", "{}" )'.format(self.ntwn_ids_and_names[node_id], p_lim_kw, p_pa, name ) )


    def add_sink(
        self, net, name, node_id, p_kw, geodata
        ):

        pg.create_load(
            net = net,
            bus = self.ntwn_ids_and_names[node_id],
            p_kW = p_kw,
            name = name
            )


    def add_station(
        self, net, name, hp_node_id, lp_node_id, p_lim_kw, p_pa
        ):

        pg.create_station(
            net = net,
            bus_high = self.ntwn_ids_and_names[hp_node_id],
            bus_low = self.ntwn_ids_and_names[lp_node_id],
            p_lim_kW = p_lim_kw,
            p_Pa = p_pa,
            name = name
            )


    def add_pipe(
        self, net, name, from_node_id, to_node_id, diameter_m, length_m, geodata
        ):

        pg.create_pipe(
            net = net,
            from_bus = self.ntwn_ids_and_names[from_node_id],
            to_bus = self.ntwn_ids_and_names[to_node_id],
            length_m = length_m,
            diameter_m = diameter_m,
            name = name
            )
