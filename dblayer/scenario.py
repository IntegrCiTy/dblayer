
class SimulationTool:
    """
    This class represents a simulation tool used in the co-simulation, including information on how it is used in this specific case (e.g., input files).
    """

    def __init__( self, name, model, image, wrapper, command = None, files = None ):
        """
        Constructor.

        :param name: name of the simulation tool (str)
        :param model: name of the model associated with the simulation tool (str)
        :param image: docker image containing environments with all the simulation tool's dependencies (str)
        :param wrapper: wrapper file for the simulation tool (str)
        :param command: optional command to add (str)
        :param files: optional files to add into the tool's docker container (list of str)
        """
        # Check if parameter 'name' is of correct type (str).
        if not isinstance( name, str ):
            raise TypeError( 'parameter \'name\' must be of type \'str\'' )

        # Check if parameter 'model' is of correct type (str).
        if not isinstance( model, str ):
            raise TypeError( 'parameter \'model\' must be of type \'str\'' )

        # Check if parameter 'image' is of correct type (str).
        if not isinstance( image, str ):
            raise TypeError( 'parameter \'image\' must be of type \'str\'' )

        # Check if parameter 'wrapper' is of correct type (str).
        if not isinstance( wrapper, str ):
            raise TypeError( 'parameter \'wrapper\' must be of type \'str\'' )

        # Check if parameter 'command' is of correct type (str).
        if ( command is not None ) and not isinstance( command, str ):
            raise TypeError( 'parameter \'command\' must be of type \'str\'' )

        # Check if parameter 'files' is of correct type (list of str).
        if ( files is not None ) and not ( isinstance( files, list ) and all( isinstance( elem, str ) for elem in files ) ):
            raise TypeError( 'parameter \'files\' must be of type \'list of str\'' )

        self.name = name
        self.model = model
        self.image = image
        self.wrapper = wrapper
        self.command = command
        self.files = files


class Port:
    """This is the subclass for input and output ports"""

    def __init__( self, variable_name, node ):
        """
        Constructor.

        :param variable_name: variable name associated to this port (str)
        :param node: node that the port is attached to (Node)
        """
        # Check if parameter 'variable_name' is of correct type (str).
        if not isinstance( variable_name, str ):
            raise TypeError( 'parameter \'variable_name\' must be of type \'str\'' )

        # Check if parameter 'node' is of correct type (Node).
        if not isinstance( node, Node ):
            raise TypeError( 'parameter \'node\' must be of type \'Node\'' )

        # Define variable name associated to port.
        self.variable_name = variable_name

        # Link port to attached node.
        self.node = node



class InputPort(Port):
    """This class represents an input port for a node"""
    pass



class OutputPort(Port):
    """This class represents an output port for a node"""
    pass



class Node:
    """This class represents co-simulation nodes"""

    def __init__( self, node_name, sim_tool, input_variable_names = None, output_variable_names = None ):
        """
        Constructor.

        :param node_name: name of this node (str)
        :param sim_tool: instance of simulation tool (SimulationTool)
        :param input_variable_names: names of input variables (list of str)
        :param output_variable_names: names of output variables (list of str)
        """
        # Check if parameter 'node_name' is of correct type (str).
        if not isinstance( node_name, str ):
            raise TypeError( 'parameter \'node_name\' must be of type \'str\'' )

        # Check if parameter 'input_variable_names' is of correct type (list of str).
        if ( sim_tool is not None ) and not isinstance( sim_tool, SimulationTool ):
            raise TypeError( 'parameter \'sim_tool\' must be of type \'SimulationTool\'' )

        # Check if parameter 'input_variable_names' is of correct type (list of str).
        if ( input_variable_names is not None ) and not ( isinstance( input_variable_names, list ) and all( isinstance( elem, str ) for elem in input_variable_names ) ):
            raise TypeError( 'parameter \'input_variable_names\' must be of type \'list of str\'' )

        # Check if parameter 'output_variable_names' is of correct type (list of str).
        if ( output_variable_names is not None ) and not ( isinstance( output_variable_names, list ) and all( isinstance( elem, str ) for elem in output_variable_names ) ):
            raise TypeError( 'parameter \'output_variable_names\' must be of type \'list of str\'' )

        # Define name.
        self.node_name = node_name

        # Initialize simulation tool.
        self.sim_tool = sim_tool

        # Initialize dicts of input ports.
        self.input_ports = {}
        if input_variable_names is not None:
            self.add_input_ports( input_variable_names )
        # Initialize dicts of outputs ports.
        self.output_ports = {}
        if output_variable_names is not None:
            self.add_output_ports( output_variable_names )


    def add_input_ports( self, input_variable_names ):
        """
        Add additional input ports for the specified variable names.

        :param input_variable_names: names of input variables (list of str)
        """
        for variable_name in input_variable_names:
            self.add_input_port( variable_name )


    def add_input_port( self, input_variable_name ):
        """
        Add additional input port for the specified variable name.

        :param input_variable_name: name of input variable (str)
        """
        # Check if parameter 'input_variable_name' is of correct type (str).
        if not isinstance( input_variable_name, str ):
            raise TypeError( 'parameter \'input_variable_name\' must be of type \'str\'' )

        # Check if input port if has been defined previously.
        if input_variable_name in self.input_ports:
            err_msg = "'{0}' is already defined as input port for node '{1}'"
            raise ValueError( err_msg.format( input_variable_name, self.node_name ) )

        # Create and add new input port.
        p = InputPort( input_variable_name, self )
        self.input_ports[ input_variable_name ] = p


    def add_output_ports( self, output_variable_names ):
        """
        Add additional output ports for the specified variable names.

        :param output_variable_names: names of output variables (list of str)
        """
        for variable_name in output_variable_names:
            self.add_output_port( variable_name )


    def add_output_port( self, output_variable_name ):
        """
        Add additional output port for the specified variable name.

        :param output_variable_name: names of output variable (str)
        """
        # Check if parameter 'output_variable_name' is of correct type (str).
        if not isinstance( output_variable_name, str ):
            raise TypeError( 'parameter \'output_variable_name\' must be of type \'str\'' )

        # Check if input port if has been defined previously.
        if output_variable_name in self.output_ports:
            err_msg = "'{0}' is already defined as output port for node '{1}'"
            raise ValueError( err_msg.format( output_variable_name, self.node_name ) )

        # Create and add new output port.
        p = OutputPort( output_variable_name, self )
        self.output_ports[ output_variable_name ] = p


    def has_input_variable( self, input_variable_name ):
        """
        Check if input port associated to variable name has been defined for this node. Returns a boolean.

        :param input_variable_name: name of input variable (str)
        """
        # Check if parameter 'input_variable_name' is of correct type (str).
        if not isinstance( input_variable_name, str ):
            raise TypeError( 'parameter \'input_variable_name\' must be of type \'str\'' )
        return ( input_variable_name in self.input_ports )


    def has_output_variable( self, output_variable_name ):
        """
        Check if output port associated to variable name has been defined for this node. Returns a boolean.

        :param output_variable_name: name of output variable (str)
        """
        # Check if parameter 'output_variable_name' is of correct type (str).
        if not isinstance( output_variable_name, str ):
            raise TypeError( 'parameter \'output_variable_name\' must be of type \'str\'' )
        return ( output_variable_name in self.output_ports )


    def get_input_port( self, input_variable_name ):
        """
        Get input port associated to variable name.

        :param input_variable_name: name of input variable (str)
        """
        # Check if an input port associated to the variable name exists.
        if not self.has_input_variable( input_variable_name ):
            err_msg = "node '{0}' has no input port assciated to '{1}'"
            raise RuntimeError( err_msg.format( self.node_name, input_variable_name ) )
        return self.input_ports[ input_variable_name ]


    def get_output_port( self, output_variable_name ):
        """
        Get output port associated to variable name.

        :param output_variable_name: name of output variable (str)
        """
        # Check if an output port associated to the variable name exists.
        if not self.has_output_variable( output_variable_name ):
            err_msg = "node '{0}' has no output port assciated to '{1}'"
            raise RuntimeError( err_msg.format( self.node_name, output_variable_name ) )
        return self.output_ports[ output_variable_name ]


class Link:
    """This class represents a link between co-simulation nodes"""

    def __init__( self, link_name, from_node, output_variable_name, to_node, input_variable_name ):
        """
        Constructor.

        :param link_name: name of link (str)
        :param from_node: node associated to output variable (Node)
        :param output_variable_name: name of output variable (str)
        :param to_node: node associated to input variable (Node)
        :param input_variable_name: name of input variable (str)
        """
        # Check if parameter 'link_name' is of correct type (str).
        if not isinstance( link_name, str ):
            raise TypeError( 'parameter \'link_name\' must be of type \'str\'' )

        # Check if parameter 'from_node' is of correct type (Node).
        if not isinstance( from_node, Node ):
            raise TypeError( 'parameter \'from_node\' must be of type \'Node\'' )

        # Check if parameter 'output_variable_name' is of correct type (str).
        if not isinstance( output_variable_name, str ):
            raise TypeError( 'parameter \'output_variable_name\' must be of type \'str\'' )

        # Check if parameter 'to_node' is of correct type (Node).
        if not isinstance( to_node, Node ):
            raise TypeError( 'parameter \'to_node\' must be of type \'Node\'' )

        # Check if parameter 'input_variable_name' is of correct type (str).
        if not isinstance( input_variable_name, str ):
            raise TypeError( 'parameter \'input_variable_name\' must be of type \'str\'' )

        # Check that 'from_node' and 'to_node' are not the same node (by name).
        if from_node.node_name == to_node.node_name:
            err_msg = "parameter 'from_node' and 'to_node' are identical (by name): '{0}'"
            raise RuntimeError( err_msg.format( from_node.node_name ) )

        # Check if node 'from_node' has an output port associated to 'output_variable_name'.
        if not from_node.has_output_variable( output_variable_name ):
            err_msg = "node '{0}' has no output variable '{1}'"
            raise RuntimeError( err_msg.format( from_node.node_name, output_variable_name ) )

        # Check if node 'to_node' has an input port associated to 'input_variable_name'.
        if not to_node.has_input_variable( input_variable_name ):
            err_msg = "node '{0}' has no input variable '{1}'"
            raise RuntimeError( err_msg.format( to_node.node_name, input_variable_name ) )

        # Define link name.
        self.link_name = link_name

        # Save links to ports.
        self.output_port = from_node.get_output_port( output_variable_name )
        self.input_port = to_node.get_input_port( input_variable_name )



class Scenario:
    """This class represents a co-simulation scenario, which provides access to all nodes and links."""

    def __init__( self, scenario_name ):
        """
        Constructor.

        :param scenario_name: name of scenario (str)
        """
        # Check if parameter 'link_name' is of correct type (str).
        if not isinstance( scenario_name, str ):
            raise TypeError( 'parameter \'scenario_name\' must be of type \'str\'' )

        # Define name.
        self.scenario_name = scenario_name

        # Initialize empty lists for nodes and links.
        self.nodes = {}
        self.links = {}


    def reset( self ):
        """
        Clear the list of nodes and links.
        """
        self.nodes.clear()
        self.links.clear()


    def get_node_names( self ):
        """
        Return the names of all nodes that have been added to the scenario.
        """
        return list( self.nodes.keys() )


    def get_node( self, node_name ):
        """
        Return the node associated to the name. Return None if no node with this name has been added to the scenario.
        """
        # Check if parameter 'link_name' is of correct type (str).
        if not isinstance( node_name, str ):
            raise TypeError( 'parameter \'node_name\' must be of type \'str\'' )

        return self.nodes[node_name] if ( node_name in self.nodes ) else None


    def get_link_names( self ):
        """
        Return the names of all links that have been added to the scenario.
        """
        return list( self.links.keys() )


    def get_link( self, link_name ):
        """
        Return the link associated to the name. Return None if no link with this name has been added to the scenario.
        """
        # Check if parameter 'link_name' is of correct type (str).
        if not isinstance( link_name, str ):
            raise TypeError( 'parameter \'link_name\' must be of type \'str\'' )

        return self.links[link_name] if ( link_name in self.links ) else None


    def add_node( self, node ):
        """
        Add an existing node to the scenario.

        :param node: node to be added (Node)
        """
        # Check if parameter 'node' is of correct type (Node).
        if not isinstance( node, Node ):
            raise TypeError( 'parameter \'node\' must be of type \'Node\'' )

        # Check if node with this name already exists.
        if node.node_name in self.nodes:
            err_msg = "node '{0}' has already been defined for scenario '{1}'"
            raise RuntimeError( err_msg.format( node.node_name, self.scenario_name ) )

        # Add node to scenario.
        self.nodes[ node.node_name ] = node


    def add_nodes( self, nodes ):
        """
        Add a list of existing nodes to the scenario.

        :param nodes: nodes to be added (list of Node)
        """
        for n in nodes: self.add_node( n )


    def create_and_add_node( self, node_name, sim_tool, input_variable_names = None, output_variable_names = None ):
        """
        Create a new node and add it to the scenario. Returns the new node.

        :param node_name: name of new node (str)
        :param sim_tool: instance of simulation tool (SimulationTool)
        :param input_variable_names: names of input variables (list of str)
        :param output_variable_names: names of output variables (list of str)
        """
        # Create a new node.
        new_node = Node( node_name, sim_tool, input_variable_names, output_variable_names )

        # Add node to scenario.
        self.add_node( new_node )

        # Return new node.
        return new_node


    def add_link( self, link ):
        """
        Add an existing link to the scenario.

        :param link: link to be added (Link)
        """
        # Check if parameter 'link' is of correct type (Link).
        if not isinstance( link, Link ):
            raise TypeError( 'parameter \'link\' must be of type \'Link\'' )

        # Check if link with this name already exists.
        if link.link_name in self.links:
            err_msg = "link '{0}' has already been defined for scenario '{1}'"
            raise RuntimeError( err_msg.format( link.link_name, self.scenario_name ) )

        # Check if start node associated to link is already in list of nodes.
        if not link.output_port.node.node_name in self.nodes:
            err_msg = "node '{0}' associated to output variable '{1}' has not been defined for scenario '{2}'"
            node_name = link.output_port.node.node_name
            variable_name = link.output_port.variable_name
            raise RuntimeError( err_msg.format( node_name, variable_name, self.scenario_name ) )

        # Check if end node associated to link is already in list of nodes.
        if not link.input_port.node.node_name in self.nodes:
            err_msg = "node '{0}' associated to input variable '{1}' has not been defined for scenario '{2}'"
            node_name = link.input_port.node.node_name
            variable_name = link.input_port.variable_name
            raise RuntimeError( err_msg.format( node_name, variable_name, self.scenario_name ) )

        # Add link to scenario.
        self.links[ link.link_name ] = link


    def add_links( self, links ):
        """
        Add existing links to the scenario.

        :param links: links to be added (list of Link)
        """
        if not ( isinstance( links, list ) and all( isinstance( elem, Link ) for elem in links ) ):
            raise TypeError( 'parameter \'links\' must be of type \'list of Link\'' )

        for l in links: self.add_link( l )


    def create_and_add_link( self, link_name, from_node, output_variable_name, to_node, input_variable_name ):
        """
        Create a new link and add it to the scenario. Returns the new link.

        :param link_name: name of link (str)
        :param from_node: name of node (str) or node itself (Node) associated to output variable
        :param output_variable_name: name of output variable (str)
        :param to_node: name of node (str) or node itself (Node) associated to input variable
        :param input_variable_name: name of input variable (str)
        """
        # Check if parameter 'link_name' is of correct type (str).
        if not isinstance( link_name, str ):
            raise TypeError( 'parameter \'link_name\' must be of type \'str\'' )

        # Check if parameter 'from_node' is of correct type (str or Node).
        if not ( isinstance( from_node, str ) or isinstance( from_node, Node ) ):
            raise TypeError( 'parameter \'from_node\' must be either of type \'str\' or \'Node\'' )

        # Check if parameter 'output_variable_name' is of correct type (str).
        if not isinstance( output_variable_name, str ):
            raise TypeError( 'parameter \'output_variable_name\' must be of type \'str\'' )

        # Check if parameter 'to_node' is of correct type (str or Node).
        if not ( isinstance( to_node, str ) or isinstance( to_node, Node ) ):
            raise TypeError( 'parameter \'to_node_name\' must be either of type \'str\' or \'Node\'' )

        # Check if parameter 'input_variable_name' is of correct type (str).
        if not isinstance( input_variable_name, str ):
            raise TypeError( 'parameter \'input_variable_name\' must be of type \'str\'' )

        # Check if link with this name already exists.
        if link_name in self.links:
            err_msg = "link '{0}' has already been defined for scenario '{1}'"
            raise RuntimeError( err_msg.format( link_name, self.scenario_name ) )

        # Retrieve name for from_node.
        from_node_name = from_node if isinstance( from_node, str ) else from_node.node_name

        # Retrieve name for to_node.
        to_node_name = to_node if isinstance( to_node, str ) else to_node.node_name

        # Check if start node associated to link is already in list of nodes.
        if not from_node_name in self.nodes:
            err_msg = "node '{0}' has not been defined for scenario '{1}'"
            raise RuntimeError( err_msg.format( from_node_name, self.scenario_name ) )

        # Check if end node associated to link is already in list of nodes.
        if not to_node_name in self.nodes:
            err_msg = "node '{0}' has not been defined for scenario '{1}'"
            raise RuntimeError( err_msg.format( to_node_name, self.scenario_name ) )

        # Retrieve nodes and create link.
        from_node = self.nodes[ from_node_name ]
        to_node = self.nodes[ to_node_name ]
        link = Link( link_name, from_node, output_variable_name, to_node, input_variable_name )

        # Add link to scenario.
        self.links[ link.link_name ] = link

        # Return new link.
        return link
