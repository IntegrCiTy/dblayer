import unittest

from datetime import datetime

from dblayer import *
from dblayer.db import *

import sqlalchemy.orm.exc



class TestPackageScenarioDB( unittest.TestCase ) :


    # Define connection parameters.
    connect = PostgreSQLConnectionInfo( 
        user = 'postgres', 
        pwd = 'postgres', 
        host = 'localhost', 
        port = '5432', 
        dbname = 'testdb'
        )

    def testScenario_cleanup_schema_1( self ):
        cleanup_schema( self.connect )


    def testScenario_read_db_1( self ):
        try:
            # Try to read a scenario that does not exist.
            scenario = read_from_db( self.connect, 'TestScenarioX' )
        except sqlalchemy.orm.exc.NoResultFound as e:
            expected_message = "No row was found for one()"
            self.assertEqual( str( e ), expected_message )


    def testScenario_write_db_1( self ):
        # Create a scenario for testing.
        scenario = Scenario( 'TestScenario1' )
        scenario.create_and_add_node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
        scenario.create_and_add_node( 'B', output_variable_names = [ 'tb' ] )
        scenario.create_and_add_node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )
        scenario.create_and_add_link( 'l1', from_node = 'A', output_variable_name = 'ta', to_node = 'C', input_variable_name = 't1' )
        scenario.create_and_add_link( 'l2', from_node = 'B', output_variable_name = 'tb', to_node = 'C', input_variable_name = 't2' )
        scenario.create_and_add_link( 'l3', from_node = 'C', output_variable_name = 'setc', to_node = 'A', input_variable_name = 'seta' )

        # Write to database.
        write_to_db( self.connect, scenario )

#         # NOT YET IMPLEMENTED: Try to write a scenario with an already existing name to database.
#         try:
#             scenario = Scenario( 'TestScenario1' )
#             write_to_db( self.connect, scenario )
#         except RuntimeError as e:
#             expected_message = ''
#             self.assertEqual( str( e ) )


    def testScenario_write_and_read_db_1( self ):
        # Define scenario name.
        scenario_name = 'TestScenario2'

        # Create a scenario that will be written to the database.
        write_scenario = Scenario( scenario_name )
        write_scenario.create_and_add_node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
        write_scenario.create_and_add_node( 'B', output_variable_names = [ 'tb' ] )
        write_scenario.create_and_add_node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )
        write_scenario.create_and_add_link( 'l1', from_node = 'A', output_variable_name = 'ta', to_node = 'C', input_variable_name = 't1' )
        write_scenario.create_and_add_link( 'l2', from_node = 'B', output_variable_name = 'tb', to_node = 'C', input_variable_name = 't2' )
        write_scenario.create_and_add_link( 'l3', from_node = 'C', output_variable_name = 'setc', to_node = 'A', input_variable_name = 'seta' )

        # Write scenario to database.
        write_to_db( self.connect, write_scenario )

        # Read scenario from database.
        read_scenario = read_from_db( self.connect, scenario_name )

        # Check node names.
        node_names = read_scenario.get_node_names()
        self.assertEqual( len( node_names ), 3 )
        self.assertTrue( 'A' in node_names )
        self.assertTrue( 'B' in node_names )
        self.assertTrue( 'C' in node_names )

        # Check link names.
        link_names = read_scenario.get_link_names()
        self.assertEqual( len( link_names ), 3 )
        self.assertTrue( 'l1' in link_names )
        self.assertTrue( 'l2' in link_names )
        self.assertTrue( 'l3' in link_names )

        # Check nodes.
        self.assertTrue( read_scenario.nodes[ 'A' ].has_input_variable( 'seta' ) )
        self.assertEqual( len( read_scenario.nodes[ 'A' ].input_ports ), 1 )
        self.assertTrue( read_scenario.nodes[ 'A' ].has_output_variable( 'ta' ) )
        self.assertEqual( len( read_scenario.nodes[ 'A' ].output_ports ), 1 )

        self.assertEqual( len( read_scenario.nodes[ 'B' ].input_ports ), 0 )
        self.assertTrue( read_scenario.nodes[ 'B' ].has_output_variable( 'tb' ) )
        self.assertEqual( len( read_scenario.nodes[ 'B' ].output_ports ), 1 )

        self.assertTrue( read_scenario.nodes[ 'C' ].has_input_variable( 't1' ) )
        self.assertTrue( read_scenario.nodes[ 'C' ].has_input_variable( 't2' ) )
        self.assertEqual( len( read_scenario.nodes[ 'C' ].input_ports ), 2 )
        self.assertTrue( read_scenario.nodes[ 'C' ].has_output_variable( 'setc' ) )
        self.assertEqual( len( read_scenario.nodes[ 'C' ].output_ports ), 1 )

        # Check links.
        self.assertEqual( read_scenario.links[ 'l1' ].output_port.node.node_name, 'A' )
        self.assertEqual( read_scenario.links[ 'l1' ].output_port.variable_name, 'ta' )
        self.assertEqual( read_scenario.links[ 'l1' ].input_port.node.node_name, 'C' )
        self.assertEqual( read_scenario.links[ 'l1' ].input_port.variable_name, 't1' )

        self.assertEqual( read_scenario.links[ 'l2' ].output_port.node.node_name, 'B' )
        self.assertEqual( read_scenario.links[ 'l2' ].output_port.variable_name, 'tb' )
        self.assertEqual( read_scenario.links[ 'l2' ].input_port.node.node_name, 'C' )
        self.assertEqual( read_scenario.links[ 'l2' ].input_port.variable_name, 't2' )

        self.assertEqual( read_scenario.links[ 'l3' ].output_port.node.node_name, 'C' )
        self.assertEqual( read_scenario.links[ 'l3' ].output_port.variable_name, 'setc' )
        self.assertEqual( read_scenario.links[ 'l3' ].input_port.node.node_name, 'A' )
        self.assertEqual( read_scenario.links[ 'l3' ].input_port.variable_name, 'seta' )


    def setUp( self ):
        self.tick = datetime.now()


    def tearDown( self ):
        self.tock = datetime.now()
        diff = self.tock - self.tick
        timing_msg = "\n[INFO] test took {0} ms\n"
        print( timing_msg.format( diff.microseconds / 1000 ) )



if __name__ == '__main__' :
    unittest.main()
