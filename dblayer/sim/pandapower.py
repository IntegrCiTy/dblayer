#!/usr/bin/env python
# coding: utf-8

from .electrical_sim_model_db_reader import ElectricalSimModelDBReader

# Import pandapower module.
import pandapower as pp


class PandaPowerModelDBReader( ElectricalSimModelDBReader ):
    """
    Construct a pandapower simulation model from information contained in the 3DCityDB.
    """

    def create_empty_network( self ):
        """
        Create an empty network model.

        :return: empty network model (pandapower.auxiliary.pandapowerNet)
        """

        return pp.create_empty_network()


    def add_bus(
            self, net, name, type, vn_kv, geodata
            ):

        pp.create_bus(
            net = net,
            name = name,
            vn_kv = vn_kv,
            type = type,
            geodata = ( geodata.x, geodata.y )
            )


    def add_line(
            self, net, name, from_bus_id, to_bus_id, type,
            c_nf_per_km, r_ohm_per_km, x_ohm_per_km, max_i_ka,
            length_km, geodata
            ):

        from_bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[from_bus_id]
            )

        to_bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[to_bus_id]
            )

        line_geodata = [ [ c.x, c.y ] for c in geodata ]

        pp.create_line_from_parameters(
                net = net,
                from_bus = from_bus,
                to_bus = to_bus,
                length_km = length_km,
                type = type,
                c_nf_per_km = c_nf_per_km,
                r_ohm_per_km = r_ohm_per_km,
                x_ohm_per_km = x_ohm_per_km,
                max_i_ka = max_i_ka,
                name = name,
                geodata = line_geodata
                )


    def add_load(
            self, net, name, bus_id, p_kw, q_kvar
            ):

        bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[bus_id]
            )

        pp.create_load(
            net = net,
            bus = bus,
            p_kw = p_kw,
            q_kvar = q_kvar,
            name = name
            )


    def add_transformer(
            self, net, name, hv_bus_id, lv_bus_id, type
            ):

        lv_bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[lv_bus_id]
            )

        hv_bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[hv_bus_id]
            )

        pp.create_transformer(
            net = net,
            hv_bus = hv_bus,
            lv_bus = lv_bus,
            std_type = type,
            name = name
            )


    def add_switch(
            self, net, name, from_bus_id, to_bus_id, type
            ):

        from_bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[from_bus_id]
            )

        to_bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[to_bus_id]
            )

        pp.create_switch(
            net = net,
            bus = from_bus,
            element = to_bus,
            et = 'b',
            closed = True,
            type = type,
            name = name
            )


    def add_ext_grid(
            self, net, name, bus_id
            ):

        bus = pp.get_element_index(
            net, 'bus', self.bus_ids_and_names[bus_id]
            )

        pp.create_ext_grid(
            net = net,
            bus = bus,
            name = name
            )
