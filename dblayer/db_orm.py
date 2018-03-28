class Simulation( object ):
    """
    Define class for retrieving data from table 'sim_pkg.simulation'.
    """
    def __init__( self, name ):
        self.name = name


class SimulationTool( object ):
    """
    Define class for retrieving data from table 'sim_pkg.tool'.
    """
    def __init__( self, name ):
        self.name = name


class Node( object ):
    """
    Define class for retrieving data from table 'sim_pkg.node'.
    """
    def __init__( self, name ):
        self.name = name


class Port( object ):
    """
    Define class for retrieving data from table 'sim_pkg.port'.
    """
    def __init__( self, name ):
        self.name = name


class PortConnectionExt( object ):
    """
    Define class for retrieving data from view 'sim_pkg.port_connection_ext'.
    """
    def __init__( self, name ):
        self.name = name


class GenericParameterTool( object ):
    """
    Define class for retrieving data from view 'sim_pkg.generic_parameter_tool'.
    """
    def __init__( self, name ):
        self.name = name


class GenericParameterNode( object ):
    """
    Define class for retrieving data from view 'sim_pkg.generic_parameter_node'.
    """
    def __init__( self, name ):
        self.name = name

        
class GenericParameterSimulation( object ):
    """
    Define class for retrieving data from view 'sim_pkg.generic_parameter_sim'.
    """
    def __init__( self, name ):
        self.name = name
