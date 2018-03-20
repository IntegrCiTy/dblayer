from dblayer import *
from dblayer.json import *
import unittest


class TestPackageScenario( unittest.TestCase ) :


    def testNode_ctor_1( self ):
        try:
            node = scenario.Node( 'Test', input_variable_names = [ 'a', 'a' ] )
        except ValueError as e:
            expected_message = "'a' is already defined as input port for node 'Test'"
            self.assertEqual( str( e ), expected_message )


    def testNode_ctor_2( self ):
        try:
            node = Node( 'Test', input_variable_names = [ 'a', 1 ] )
        except TypeError as e:
            expected_message = "parameter 'input_variable_name' must be of type 'str'"
            self.assertEqual( str( e ), expected_message )


    def testNode_ctor_3( self ):
        try:
            node = Node( 'Test', output_variable_names = [ 'a', 'a' ] )
        except ValueError as e:
            expected_message = "'a' is already defined as output port for node 'Test'"
            self.assertEqual( str( e ), expected_message )


    def testNode_ctor_4( self ):
        try:
            node = Node( 'Test', output_variable_names = [ 'b', 2 ] )
        except TypeError as e:
            expected_message = "parameter 'output_variable_name' must be of type 'str'"
            self.assertEqual( str( e ), expected_message )


    def testNode_has_input_variable( self ):
        node_with_inputs = Node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        self.assertEqual( node_with_inputs.has_input_variable( 'b' ), True )
        self.assertEqual( node_with_inputs.has_input_variable( 'c' ), False )


    def testNode_has_output_variable( self ):
        node_with_outputs = Node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        self.assertEqual( node_with_outputs.has_output_variable( 'B' ), True )
        self.assertEqual( node_with_outputs.has_output_variable( 'C' ), False )


    def testNode_get_input_port_1( self ):
        node_with_inputs = Node( 'TestNode', input_variable_names = [ 'a' ] )
        port = node_with_inputs.get_input_port( 'a' )
        self.assertEqual( port.variable_name, 'a' )
        self.assertEqual( port.node, node_with_inputs )
        

    def testNode_get_input_port_2( self ):
        node_with_inputs = Node( 'TestNode' )
        try:
            port = node_with_inputs.get_input_port( 'a' )
        except RuntimeError as e:
            expected_message = "node 'TestNode' has no input port assciated to 'a'"
            self.assertEqual( str( e ), expected_message )


    def testNode_get_output_port_1( self ):
        node_with_outputs = Node( 'TestNode', output_variable_names = [ 'A' ] )
        port = node_with_outputs.get_output_port( 'A' )
        self.assertEqual( port.variable_name, 'A' )
        self.assertEqual( port.node, node_with_outputs )
        

    def testNode_get_output_port_2( self ):
        node_with_outputs = Node( 'TestNode' )
        try:
            port = node_with_outputs.get_output_port( 'A' )
        except RuntimeError as e:
            expected_message = "node 'TestNode' has no output port assciated to 'A'"
            self.assertEqual( str( e ), expected_message )


    def testLink_ctor_1( self ):
        node_with_inputs = Node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = Node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        link = Link( 'TestLink', node_with_outputs, 'A', node_with_inputs, 'a' )


    def testLink_ctor_2( self ):
        try:
            link = Link( 'TestLink', Node( 'TestNode' ), 'a', Node( 'TestNode' ), 'a' )
        except RuntimeError as e:
            expected_message = "parameter 'from_node' and 'to_node' are identical (by name): 'TestNode'"
            self.assertEqual( str( e ), expected_message )


    def testLink_ctor_3( self ):
        try:
            link = Link( 'TestLink', Node( 'TestNode1' ), 'a', Node( 'TestNode2', input_variable_names = [ 'a' ] ), 'a' )
        except RuntimeError as e:
            expected_message = "node 'TestNode1' has no output variable 'a'"
            self.assertEqual( str( e ), expected_message )


    def testLink_ctor_4( self ):
        try:
            link = Link( 'TestLink', Node( 'TestNode1', output_variable_names = [ 'a' ] ), 'a', Node( 'TestNode2' ), 'a' )
        except RuntimeError as e:
            expected_message = "node 'TestNode2' has no input variable 'a'"
            self.assertEqual( str( e ), expected_message )


    def testLink_ctor_5( self ):
        try:
            link = Link( 'TestLink', 'TestNode1', 'A', Node( 'TestNode2', input_variable_names = [ 'a' ] ), 'a' )
        except TypeError as e:
            expected_message = "parameter 'from_node' must be of type 'Node'"
            self.assertEqual( str( e ), expected_message )


    def testLink_ctor_6( self ):
        try:
            link = Link( 'TestLink', Node( 'TestNode1', output_variable_names = [ 'a' ] ), 'A', 'TestNode2', 'a' )
        except TypeError as e:
            expected_message = "parameter 'to_node' must be of type 'Node'"
            self.assertEqual( str( e ), expected_message )


    def testLink_ctor_7( self ):
        try:
            link = Link( 1, Node( 'TestNode1' ), 'A', Node( 'TestNode2' ), 'a' )
        except TypeError as e:
            expected_message = "parameter 'link_name' must be of type 'str'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_ctor_1( self ):
        scenario = Scenario( 'TestScenario' )


    def testScenario_ctor_2( self ):
        try:
            scenario = Scenario( Node( 'TestNode' ) )
        except TypeError as e:
            expected_message = "parameter 'scenario_name' must be of type 'str'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_node_1( self ):
        scenario = Scenario( 'TestScenario' )
        scenario.add_node( Node( 'TestNode' ) )


    def testScenario_add_node_2( self ):
        scenario = Scenario( 'TestScenario' )
        try:
            scenario.add_node( 'TestNode' )
        except TypeError as e:
            expected_message = "parameter 'node' must be of type 'Node'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_nodes_1( self ):
        scenario = Scenario( 'TestScenario' )
        try:
            scenario.add_nodes( [ Node( 'TestNode' ), 'TestNode' ] )
        except TypeError as e:
            expected_message = "parameter 'node' must be of type 'Node'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_nodes_2( self ):
        scenario = Scenario( 'TestScenario' )
        try:
            scenario.reset()
            scenario.add_nodes( [ Node( 'TestNode' ), Node( 'TestNode' ) ] )
        except RuntimeError as e:
            expected_message = "node 'TestNode' has already been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_1( self ):
        node_with_inputs = Node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = Node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        link = Link( 'TestLink', node_with_outputs, 'A', node_with_inputs, 'a' )
        scenario = Scenario( 'TestScenario' )
        try:
            scenario.add_link( link )
        except RuntimeError as e:
            expected_message = "node 'TestNodeWithOutputs' associated to output variable 'A' has not been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_2( self ):
        node_with_inputs = Node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = Node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        link = Link( 'TestLink', node_with_outputs, 'A', node_with_inputs, 'a' )
        scenario = Scenario( 'TestScenario' )
        scenario.add_node( node_with_inputs )
        try:
            scenario.add_link( link )
        except RuntimeError as e:
            expected_message = "node 'TestNodeWithOutputs' associated to output variable 'A' has not been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_3( self ):
        node_with_inputs = Node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = Node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        link = Link( 'TestLink', node_with_outputs, 'A', node_with_inputs, 'a' )
        scenario = Scenario( 'TestScenario' )
        scenario.add_node( node_with_inputs )
        try:
            scenario.add_link( link )
        except RuntimeError as e:
            expected_message = "node 'TestNodeWithOutputs' associated to output variable 'A' has not been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_4( self ):
        node_with_inputs = Node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = Node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        link = Link( 'TestLink', node_with_outputs, 'A', node_with_inputs, 'a' )
        scenario = Scenario( 'TestScenario' )
        scenario.add_node( node_with_outputs )
        try:
            scenario.add_link( link )
        except RuntimeError as e:
            expected_message = "node 'TestNodeWithInputs' associated to input variable 'a' has not been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_5( self ):
        node_with_inputs = Node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = Node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        link = Link( 'TestLink', node_with_outputs, 'A', node_with_inputs, 'a' )
        scenario = Scenario( 'TestScenario' )
        scenario.add_node( node_with_inputs )
        scenario.add_node( node_with_outputs )
        scenario.add_link( link )
        try:
            scenario.add_link( link )
        except RuntimeError as e:
            expected_message = "link 'TestLink' has already been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_6( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        link = Link( 'TestLink', node_with_outputs, 'A', node_with_inputs, 'a' )
        scenario.add_link( link )
        try:
            scenario.add_link( link )
        except RuntimeError as e:
            expected_message = "link 'TestLink' has already been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_7( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        try:
            scenario.create_and_add_link( 1, 'TestNodeWithOutputs', 'A', 'TestNodeWithInputs', 'a' )
        except TypeError as e:
            expected_message = "parameter 'link_name' must be of type 'str'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_8( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        scenario.create_and_add_link( 'TestLink', node_with_outputs, 'A', 'TestNodeWithInputs', 'a' )


    def testScenario_add_link_9( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        try:
            scenario.create_and_add_link( 'TestLink', 'TestNodeWithOutputs', 1, 'TestNodeWithInputs', 'a' )
        except TypeError as e:
            expected_message = "parameter 'output_variable_name' must be of type 'str'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_10( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        scenario.create_and_add_link( 'TestLink', 'TestNodeWithOutputs', 'A', node_with_inputs, 'a' )


    def testScenario_add_link_11( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        try:
            scenario.create_and_add_link( 'TestLink', 'TestNodeWithOutputs', 'A', 'TestNodeWithInputs', 1 )
        except TypeError as e:
            expected_message = "parameter 'input_variable_name' must be of type 'str'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_add_link_12( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        scenario.create_and_add_link( 'TestLink', 'TestNodeWithOutputs', 'A', 'TestNodeWithInputs', 'a' )
        try:
            scenario.create_and_add_link( 'TestLink', 'TestNodeWithOutputs', 'A', 'TestNodeWithInputs', 'a' )
        except RuntimeError as e:
            expected_message = "link 'TestLink' has already been defined for scenario 'TestScenario'"
            self.assertEqual( str( e ), expected_message )


    def testScenario_get_node_names( self ):
        scenario = Scenario( 'TestScenario' )
        scenario.create_and_add_node( 'TestNode' )
        node_names = scenario.get_node_names()
        self.assertEqual( len( node_names ), 1 )
        self.assertEqual( node_names[0], 'TestNode' )


    def testScenario_get_node( self ):
        scenario = Scenario( 'TestScenario' )
        scenario.create_and_add_node( 'TestNode' )
        node = scenario.get_node( 'TestNode' )
        self.assertNotEqual( node, None )
        self.assertEqual( node.node_name, 'TestNode' )


    def testScenario_get_link_names( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        scenario.create_and_add_link( 'TestLink', 'TestNodeWithOutputs', 'A', 'TestNodeWithInputs', 'a' )
        link_names = scenario.get_link_names()
        self.assertEqual( len( link_names ), 1 )
        self.assertEqual( link_names[0], 'TestLink' )


    def testScenario_get_link( self ):
        scenario = Scenario( 'TestScenario' )
        node_with_inputs = scenario.create_and_add_node( 'TestNodeWithInputs', input_variable_names = [ 'a', 'b' ] )
        node_with_outputs = scenario.create_and_add_node( 'TestNodeWithOutputs', output_variable_names = [ 'A', 'B' ] )
        scenario.create_and_add_link( 'TestLink', 'TestNodeWithOutputs', 'A', 'TestNodeWithInputs', 'a' )
        link = scenario.get_link( 'TestLink' )
        self.assertNotEqual( link, None )
        self.assertEqual( link.link_name, 'TestLink' )


    def testScenario_write_json_1( self ):
        # Create scenario.
        scenario = Scenario( 'TestScenario' )
        scenario.create_and_add_node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
        scenario.create_and_add_node( 'B', output_variable_names = [ 'tb' ] )
        scenario.create_and_add_node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )
        scenario.create_and_add_link( 'l1', from_node = 'A', output_variable_name = 'ta', to_node = 'C', input_variable_name = 't1' )
        scenario.create_and_add_link( 'l2', from_node = 'B', output_variable_name = 'tb', to_node = 'C', input_variable_name = 't2' )
        scenario.create_and_add_link( 'l3', from_node = 'C', output_variable_name = 'setc', to_node = 'A', input_variable_name = 'seta' )

        # Dump scenario to JSON string.
        json_scenario_dump = dump_to_json_string( scenario )

        # Open file containing JSON string.
        json_file = open( 'test.json' )

        # Load JSON string from file for comparison.
        json_scenario_dump_compare = json_file.read()

        # Close file.
        json_file.close()

        # Decode both JSON strings into Python objects.
        scenario_dump_compare = json.loads( json_scenario_dump_compare )
        scenario_dump = json.loads( json_scenario_dump )

        # Define helper function that searches for lists in dicts and sorts them.
        def sort_lists_in_dict( d ):
            for key, value in d.items():
                if isinstance( value, dict ):
                    sort_lists_in_dict( value )
                elif isinstance( value, list ):
                    value.sort()

        # Sort lists in data structures, in order to make them easily comparable.
        sort_lists_in_dict( scenario_dump_compare )
        sort_lists_in_dict( scenario_dump )

        # Check for equality.
        self.assertEqual( scenario_dump_compare, scenario_dump )


    def testScenario_read_json_1( self ):
        # Read scenario from JSON-formatted file.
        scenario = read_from_json_file( 'test.json', 'TestScenario' )

        # Check node names.
        node_names = scenario.get_node_names()
        self.assertEqual( len( node_names ), 3 )
        self.assertTrue( 'A' in node_names )
        self.assertTrue( 'B' in node_names )
        self.assertTrue( 'C' in node_names )

        # Check link names.
        link_names = scenario.get_link_names()
        self.assertEqual( len( link_names ), 3 )
        self.assertTrue( 'l1' in link_names )
        self.assertTrue( 'l2' in link_names )
        self.assertTrue( 'l3' in link_names )

        # Check nodes.
        self.assertTrue( scenario.nodes[ 'A' ].has_input_variable( 'seta' ) )
        self.assertEqual( len( scenario.nodes[ 'A' ].input_ports ), 1 )
        self.assertTrue( scenario.nodes[ 'A' ].has_output_variable( 'ta' ) )
        self.assertEqual( len( scenario.nodes[ 'A' ].output_ports ), 1 )

        self.assertEqual( len( scenario.nodes[ 'B' ].input_ports ), 0 )
        self.assertTrue( scenario.nodes[ 'B' ].has_output_variable( 'tb' ) )
        self.assertEqual( len( scenario.nodes[ 'B' ].output_ports ), 1 )

        self.assertTrue( scenario.nodes[ 'C' ].has_input_variable( 't1' ) )
        self.assertTrue( scenario.nodes[ 'C' ].has_input_variable( 't2' ) )
        self.assertEqual( len( scenario.nodes[ 'C' ].input_ports ), 2 )
        self.assertTrue( scenario.nodes[ 'C' ].has_output_variable( 'setc' ) )
        self.assertEqual( len( scenario.nodes[ 'C' ].output_ports ), 1 )

        # Check links.
        self.assertEqual( scenario.links[ 'l1' ].output_port.node.node_name, 'A' )
        self.assertEqual( scenario.links[ 'l1' ].output_port.variable_name, 'ta' )
        self.assertEqual( scenario.links[ 'l1' ].input_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l1' ].input_port.variable_name, 't1' )

        self.assertEqual( scenario.links[ 'l2' ].output_port.node.node_name, 'B' )
        self.assertEqual( scenario.links[ 'l2' ].output_port.variable_name, 'tb' )
        self.assertEqual( scenario.links[ 'l2' ].input_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l2' ].input_port.variable_name, 't2' )

        self.assertEqual( scenario.links[ 'l3' ].output_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l3' ].output_port.variable_name, 'setc' )
        self.assertEqual( scenario.links[ 'l3' ].input_port.node.node_name, 'A' )
        self.assertEqual( scenario.links[ 'l3' ].input_port.variable_name, 'seta' )


    def testScenario_createScenario_1( self ):
        # Create scenario.
        scenario = Scenario( 'TestScenario' )
        scenario.create_and_add_node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
        scenario.create_and_add_node( 'B', output_variable_names = [ 'tb' ] )
        scenario.create_and_add_node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )
        scenario.create_and_add_link( 'l1', from_node = 'A', output_variable_name = 'ta', to_node = 'C', input_variable_name = 't1' )
        scenario.create_and_add_link( 'l2', from_node = 'B', output_variable_name = 'tb', to_node = 'C', input_variable_name = 't2' )
        scenario.create_and_add_link( 'l3', from_node = 'C', output_variable_name = 'setc', to_node = 'A', input_variable_name = 'seta' )
        # Read scenario from JSON-formatted file.

        # Check node names.
        node_names = scenario.get_node_names()
        self.assertEqual( len( node_names ), 3 )
        self.assertTrue( 'A' in node_names )
        self.assertTrue( 'B' in node_names )
        self.assertTrue( 'C' in node_names )

        # Check link names.
        link_names = scenario.get_link_names()
        self.assertEqual( len( link_names ), 3 )
        self.assertTrue( 'l1' in link_names )
        self.assertTrue( 'l2' in link_names )
        self.assertTrue( 'l3' in link_names )

        # Check nodes.
        self.assertTrue( scenario.nodes[ 'A' ].has_input_variable( 'seta' ) )
        self.assertEqual( len( scenario.nodes[ 'A' ].input_ports ), 1 )
        self.assertTrue( scenario.nodes[ 'A' ].has_output_variable( 'ta' ) )
        self.assertEqual( len( scenario.nodes[ 'A' ].output_ports ), 1 )

        self.assertEqual( len( scenario.nodes[ 'B' ].input_ports ), 0 )
        self.assertTrue( scenario.nodes[ 'B' ].has_output_variable( 'tb' ) )
        self.assertEqual( len( scenario.nodes[ 'B' ].output_ports ), 1 )

        self.assertTrue( scenario.nodes[ 'C' ].has_input_variable( 't1' ) )
        self.assertTrue( scenario.nodes[ 'C' ].has_input_variable( 't2' ) )
        self.assertEqual( len( scenario.nodes[ 'C' ].input_ports ), 2 )
        self.assertTrue( scenario.nodes[ 'C' ].has_output_variable( 'setc' ) )
        self.assertEqual( len( scenario.nodes[ 'C' ].output_ports ), 1 )

        # Check links.
        self.assertEqual( scenario.links[ 'l1' ].output_port.node.node_name, 'A' )
        self.assertEqual( scenario.links[ 'l1' ].output_port.variable_name, 'ta' )
        self.assertEqual( scenario.links[ 'l1' ].input_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l1' ].input_port.variable_name, 't1' )

        self.assertEqual( scenario.links[ 'l2' ].output_port.node.node_name, 'B' )
        self.assertEqual( scenario.links[ 'l2' ].output_port.variable_name, 'tb' )
        self.assertEqual( scenario.links[ 'l2' ].input_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l2' ].input_port.variable_name, 't2' )

        self.assertEqual( scenario.links[ 'l3' ].output_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l3' ].output_port.variable_name, 'setc' )
        self.assertEqual( scenario.links[ 'l3' ].input_port.node.node_name, 'A' )
        self.assertEqual( scenario.links[ 'l3' ].input_port.variable_name, 'seta' )


    def testScenario_createScenario_2( self ):
        # Create scenario.
        scenario = Scenario( 'TestScenario' )

        nodeA = Node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
        nodeB = Node( 'B', output_variable_names = [ 'tb' ] )
        nodeC = Node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )

        link1 = Link( 'l1', from_node = nodeA, output_variable_name = 'ta', to_node = nodeC, input_variable_name = 't1' )
        link2 = Link( 'l2', from_node = nodeB, output_variable_name = 'tb', to_node = nodeC, input_variable_name = 't2' )
        link3 = Link( 'l3', from_node = nodeC, output_variable_name = 'setc', to_node = nodeA, input_variable_name = 'seta' )

        scenario.add_node( nodeA )
        scenario.add_node( nodeB )
        scenario.add_node( nodeC )

        scenario.add_link( link1 )
        scenario.add_link( link2 )
        scenario.add_link( link3 )

        # Check node names.
        node_names = scenario.get_node_names()
        self.assertEqual( len( node_names ), 3 )
        self.assertTrue( 'A' in node_names )
        self.assertTrue( 'B' in node_names )
        self.assertTrue( 'C' in node_names )

        # Check link names.
        link_names = scenario.get_link_names()
        self.assertEqual( len( link_names ), 3 )
        self.assertTrue( 'l1' in link_names )
        self.assertTrue( 'l2' in link_names )
        self.assertTrue( 'l3' in link_names )

        # Check nodes.
        self.assertTrue( scenario.nodes[ 'A' ].has_input_variable( 'seta' ) )
        self.assertEqual( len( scenario.nodes[ 'A' ].input_ports ), 1 )
        self.assertTrue( scenario.nodes[ 'A' ].has_output_variable( 'ta' ) )
        self.assertEqual( len( scenario.nodes[ 'A' ].output_ports ), 1 )

        self.assertEqual( len( scenario.nodes[ 'B' ].input_ports ), 0 )
        self.assertTrue( scenario.nodes[ 'B' ].has_output_variable( 'tb' ) )
        self.assertEqual( len( scenario.nodes[ 'B' ].output_ports ), 1 )

        self.assertTrue( scenario.nodes[ 'C' ].has_input_variable( 't1' ) )
        self.assertTrue( scenario.nodes[ 'C' ].has_input_variable( 't2' ) )
        self.assertEqual( len( scenario.nodes[ 'C' ].input_ports ), 2 )
        self.assertTrue( scenario.nodes[ 'C' ].has_output_variable( 'setc' ) )
        self.assertEqual( len( scenario.nodes[ 'C' ].output_ports ), 1 )

        # Check links.
        self.assertEqual( scenario.links[ 'l1' ].output_port.node.node_name, 'A' )
        self.assertEqual( scenario.links[ 'l1' ].output_port.variable_name, 'ta' )
        self.assertEqual( scenario.links[ 'l1' ].input_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l1' ].input_port.variable_name, 't1' )

        self.assertEqual( scenario.links[ 'l2' ].output_port.node.node_name, 'B' )
        self.assertEqual( scenario.links[ 'l2' ].output_port.variable_name, 'tb' )
        self.assertEqual( scenario.links[ 'l2' ].input_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l2' ].input_port.variable_name, 't2' )

        self.assertEqual( scenario.links[ 'l3' ].output_port.node.node_name, 'C' )
        self.assertEqual( scenario.links[ 'l3' ].output_port.variable_name, 'setc' )
        self.assertEqual( scenario.links[ 'l3' ].input_port.node.node_name, 'A' )
        self.assertEqual( scenario.links[ 'l3' ].input_port.variable_name, 'seta' )

if __name__ == '__main__' :
    unittest.main()
