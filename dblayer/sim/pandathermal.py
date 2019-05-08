from .thermal_sim_model_db_reader import ThermalSimModelDBReader

# Import pandathermal module.
import pandathermal as pth

import warnings


class PandaThermalModelDBReader( ThermalSimModelDBReader ):
    """
    Construct a pandathermal simulation model from information contained in the 3DCityDB.
    """

    def create_empty_network( self ):
        """
        Create an empty network model.

        :return: empty network model (networkx.classes.digraph.DiGraph)
        """

        return pth.create_empty_directed_network()


    def add_thermal_source(
        self, net, name, geodata
        ):

        if self.verbose: print( 'pth.add_srce( net, "{}" )'.format(name) )

        pth.add_srce( net, name )


    def add_sink(
        self, net, name, heat_diss_kw, geodata
        ):

        if self.verbose: print( 'pth.add_sink( net, "{}", p_kw = {} )'.format( name, heat_diss_kw ) )

        pth.add_sink( net, name, p_kw = heat_diss_kw )


    def add_junction(
        self, net, name, geodata
        ):

        if self.verbose: print( 'pth.add_node( net, "{}" )'.format(name) )

        pth.add_node( net, name )


    def add_pipe(
        self, net, name, from_node_id, to_node_id, length_km, geodata
        ):

        from_node_name = self.feature_names[from_node_id]
        to_node_name = self.feature_names[to_node_id]

        if self.verbose: print( 'pth.add_pipe( net, "{}", "{}" )'.format( from_node_name, to_node_name ) )

        pth.add_pipe( net, from_node_name, to_node_name )
