from .access import *
from .db_func import *

import ictdeploy

import pandas
import json


class DBWriter( DBAccess ):
    """
    Helper class for writing simulation setups to a database.
    Requires the Simulation Package schema to be installed.
    """

    def __init__( self, sim ):
        """
        Constructor.

        :param sim: simulation setup to be read/written to database (ictdeploy.Simulator)
        """
        super().__init__()

        if not isinstance( sim, ictdeploy.Simulator ):
            raise TypeError( 'parameter \'sim\' must be of type \'ictdeploy.Simulator\'' )

        # Data from simulation setup.
        self.sim = sim

        # Dicts for collectiong database IDs.
        self.meta_model_ids = {}
        self.model_ids = {}
        self.attribute_ids = {}


    def write_to_db( self, sim_name, connect, write_meta_models = True, write_models = True  ):
        """
        Write simulator setup to database.

        :param sim_name: name used to identify this simulation setup in the database (str)
        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        :return: none
        """
        if not isinstance( sim_name, str ):
            raise TypeError( 'parameter \'sim_name\' must be of type \'str\'' )

        if not isinstance( connect, PostgreSQLConnectionInfo ):
            raise TypeError( 'parameter \'connect\' must be of type \'PostgreSQLConnectionInfo\'' )

        # Connect to database.
        engine, session = self.connect_to_db( connect )

        if ( write_meta_models is False ) or ( write_models is False ):
            # Initialize object relational mapper.
            self.init_orm( engine )

        # Start session.
        s = session()

        sim_id = self._write_simulation_to_db( sim_name, s )

        # Iterate through the meta models of the simulation setup.
        for meta_name, meta_model in self.sim.edit.meta_models.items():
            if ( write_meta_models == True ):
                # Insert meta model into the database (stored as simulation tool).
                self._write_meta_model_to_db( meta_name, meta_model, s )
            else:
                # Retrieve meta model from the database (stored as simulation tool).
                self._retrieve_meta_model_from_db( meta_name, s )


        # Iterate through the models of the simulation setup.
        for model_name, model in self.sim.edit.models.items():
            if ( write_models == True ):
                # Insert model into the database (stored as simulation tool).
                self._write_model_to_db( model_name, model, s )
            else:
                # Retrieve model from the database (stored as simulation tool).
                self._retrieve_model_from_db( model_name, s )

        # Iterate through the nodes of the simulation setup.
        for node_name in self.sim.edit.nodes.index:
            node = self.sim.edit.nodes.loc[ node_name ]
            # Insert node into the database.
            self._write_node_to_db( node_name, node, sim_id, s )

        # Iterate through the scenario's links.
        for link_index in self.sim.edit.links.index:
            link_name = str( 'link' ) + str( link_index )
            link = self.sim.edit.links.loc[ link_index ]
            # Insert link into the database (stored as port connection).
            self._write_link_to_db( link_name, link, sim_id, s )

        # Commit session.
        s.commit()

        # Close session.
        session.close_all()


    def _write_simulation_to_db( self, sim_name, session ):
        # Define function call to insert simulation to database.
        insert_sim = func_insert_simulation( sim_name )

        # Store simulation and retrieve the ID of its database representation.
        sim_query = session.query( insert_sim ).one()
        sim_id = sim_query[0]

        # Store simulation sequence as JSON-formatted generic string parameter.
        str_sequence = json.dumps( self.sim.sequence, sort_keys = False, separators = ( ',', ': ' ) )
        insert_sequence = func_insert_string_parameter_simulation( sim_id, 'sequence', str_sequence )
        session.query( insert_sequence ).one()

        # Return simulation time steps as numeric array generic parameter.
        insert_steps = func_insert_array_parameter_simulation( sim_id, 'steps', self.sim.steps, 's' )
        session.query( insert_steps ).one()

        return sim_id


    def _write_meta_model_to_db( self, meta_name, meta_model, session ):
        # Define function call to insert meta model to database (stored as template node).
        insert_meta = func_insert_node_template( meta_name )

        # Store meta model and retrieve the ID of its database representation.
        result = session.query( insert_meta ).one()
        meta_id = result[0]

        for input_name in meta_model[ 'set_attrs' ]:
            # Define function call to insert input attribute to database (stored as input port).
            insert_set_attr = func_insert_port( meta_id, 'input', input_name )

            # Store input attribute.
            session.query( insert_set_attr ).one()

        for output_name in meta_model[ 'get_attrs' ]:
            # Define function call to insert output attribute to database (stored as output port).
            insert_get_attr = func_insert_port( meta_id, 'output', output_name )

            # Store output attribute.
            session.query( insert_get_attr ).one()

        # Collect meta model ID.
        self.meta_model_ids[ meta_name ] = meta_id


    def _retrieve_meta_model_from_db( self, meta_name, s ):
        meta_model = s.query( Node ).filter( and_( Node.name == meta_name, Node.is_template == True ) ).one()
        self.meta_model_ids[ meta_name ] = meta_model.id


    def _write_model_to_db( self, model_name, model, session ):
        # Define function call to insert model into the database (stored as simulation tool).
        insert_model = func_insert_tool( model_name )

        # Store model and retrieve the ID of its database representation.
        result = session.query( insert_model ).one()
        model_id = result[0]

        # Store 'meta' attribute as generic parameter.
        insert_meta = func_insert_string_parameter_tool( model_id, 'meta', model[ 'meta' ] )
        session.query( insert_meta ).one()

        # Store 'image' attribute as generic parameter.
        insert_image = func_insert_string_parameter_tool( model_id, 'image', model[ 'image' ] )
        session.query( insert_image ).one()

        # Store 'wrapper' attribute as generic parameter.
        insert_wrapper = func_insert_string_parameter_tool( model_id, 'wrapper', model[ 'wrapper' ] )
        session.query( insert_wrapper ).one()

        # Store 'command' attribute as generic parameter.
        if model[ 'command' ] is not None:
            insert_command = func_insert_string_parameter_tool( model_id, 'command', model[ 'command' ] )
            session.query( insert_command ).one()

        # Store 'files' attribute as generic parameter.
        if model[ 'files' ] is not None:
            # Convert list of strings to JSON-formatted string.
            str_files = json.dumps( model[ 'files' ], sort_keys = False, separators = ( ',', ': ' ) )
            # Now store it as string.
            insert_files = func_insert_string_parameter_tool( model_id, 'files', str_files )
            session.query( insert_files ).one()

        # Collect model ID.
        self.model_ids[ model_name ] = model_id


    def _retrieve_model_from_db( self, model_name, s ):
        model = s.query( SimulationTool ).filter_by( name = model_name ).one()
        self.model_ids[ model_name ] = model.id


    def _write_node_to_db( self, node_name, node, sim_id, session ):
        # Retrieve meta model ID.
        meta_name = node[ 'meta' ]
        meta_id = self.meta_model_ids[ meta_name ]

        # Retrieve model ID.
        model_name = node[ 'model' ]
        model_id = self.model_ids[ model_name ]

        # Define function call to insert node to database.
        insert_node = func_insert_node( node_name, sim_id, model_id, meta_id )

        # Store node and retrieve the ID of its database representation.
        result = session.query( insert_node ).one()
        node_id = result[0]

        # Store 'is_first' attribute as generic parameter.
        insert_is_first = func_insert_string_parameter_node( node_id, 'is_first', str( node[ 'is_first' ] ) )
        session.query( insert_is_first ).one()

        self._write_node_init_vals_to_db( node_id, node[ 'init_values' ], session )

        input_ids = {}
        output_ids = {}

        meta_model = self.sim.edit.meta_models[ meta_name ]

        for input_name in meta_model[ 'set_attrs' ]:
            # Define function call to insert input attribute to database (stored as input port).
            insert_port = func_insert_port( node_id, 'input', input_name )

            # Store port and retrieve the ID of its database representation.
            result = session.query( insert_port ).one()
            input_id = result[0]

            # Save the ID (may be needed when saving links).
            input_ids[ input_name ] = input_id

        for output_name in meta_model[ 'get_attrs' ]:
            # Define function call to insert output attribute to database (stored as output port).
            insert_port = func_insert_port( node_id, 'output', output_name )

            # Store port and retrieve the ID of its database representation.
            result = session.query( insert_port ).one()
            output_id = result[0]

            # Save the ID (may be needed when saving links).
            output_ids[ output_name ] = output_id

        # Collect data about all input/output IDs for this node.
        self.attribute_ids[ node_name ] = { 'inputs' : input_ids, 'outputs' : output_ids }


    def _write_node_init_vals_to_db( self, node_id, init_vals, session ):
        for name, value in init_vals.items():
            func_insert_init_val = None

            if isinstance( value, float ):
                func_insert_init_val = func_insert_real_init_val_node( node_id, name, value )
            elif isinstance( value, int ):
                func_insert_init_val = func_insert_integer_init_val_node( node_id, name, value )
            elif isinstance( value, str ):
                func_insert_init_val = func_insert_string_init_val_node( node_id, name, value )
            elif isinstance( value, bool ):
                func_insert_init_val = func_insert_string_init_val_node( node_id, name, str( value ) )
            else:
                func_insert_init_val = func_insert_string_init_val_node( node_id, name, str( value ) )

            session.query( func_insert_init_val ).one()


    def _write_link_to_db( self, link_name, link, sim_id, session ):
        # Retrieve information about the link's output attribute.
        get_node_name = link[ 'get_node' ]
        get_attribute_name = link[ 'get_attr' ]
        get_attribute_id = self.attribute_ids[ get_node_name ][ 'outputs' ][ get_attribute_name ]

        # Retrieve information about the link's input attribute.
        set_node_name = link[ 'set_node' ]
        set_attribute_name = link[ 'set_attr' ]
        set_attribute_id = self.attribute_ids[ set_node_name ][ 'inputs' ][ set_attribute_name ]

        # Define function call to insert link to database (stored as port connection).
        insert_link = func_insert_port_connection( sim_id, link_name, get_attribute_id, set_attribute_id )

        # Store link and retrieve the ID of its database representation.
        result = session.query( insert_link ).one()
        link_id = result[0]
