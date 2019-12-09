from .associate import *
from dblayer.access import *
from dblayer.func.func_simpkg import *

import zerobnl

import pandas
import json

import pathlib
import os.path


class DBWriter( DBAccess ):
    """
    Helper class for writing ZerOBNL simulation setups to a database.
    Requires the Simulation Package schema to be installed.
    """

    def __init__( self, connect ):
        """
        Constructor.

        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        """
        super().__init__()

        if not isinstance( connect, PostgreSQLConnectionInfo ):
            raise TypeError( 'parameter \'connect\' must be of type \'PostgreSQLConnectionInfo\'' )

        # Connect to database.
        self.connect_to_citydb( connect )

        # Dicts for collectiong database IDs.
        self.meta_model_ids = {}
        self.env_ids = {}
        self.attribute_ids = {}


    def write_to_db( self, sim, sim_name, write_meta_models = True, write_envs = True  ):
        """
        Write simulator setup to database.

        :param sim: simulation setup to be read/written to database (ictdeploy.Simulator)
        :param sim_name: name used to identify this simulation setup in the database (str)
        :return: none
        """
        if not isinstance( sim, zerobnl.CoSim ):
            raise TypeError( 'parameter \'sim\' must be of type \'ictdeploy.Simulator\'' )

        if not isinstance( sim_name, str ):
            raise TypeError( 'parameter \'sim_name\' must be of type \'str\'' )

        if ( write_meta_models is False ) or ( write_envs is False ):
            # Initialize object relational mapper for reading available (meta) models.
            self._init_simpkg_orm()

        # Data from simulation setup.
        self.sim = sim

        # Start session.
        if self.current_session is None: self.start_citydb_session()

        sim_id = self._write_simulation_to_db( sim_name )

        # Iterate through the meta models of the simulation setup.
        for meta_name, meta_model in self.sim.meta_models.items():
            if ( write_meta_models == True ):
                # Insert meta model into the database (stored as simulation tool).
                self._write_meta_model_to_db( meta_name, meta_model )
            else:
                # Retrieve meta model from the database (stored as simulation tool).
                self._retrieve_meta_model_from_db( meta_name )


        # Iterate through the environments of the simulation setup.
        for env_name, env in self.sim.environments.items():
            if ( write_envs == True ):
                # Insert environment into the database (stored as simulation tool).
                self._write_env_to_db( env_name, env )
            else:
                # Retrieve environment from the database (stored as simulation tool).
                self._retrieve_env_from_db( env_name )

        # Iterate through the nodes of the simulation setup.
        for node_index, node in self.sim.nodes.iterrows():
            # Insert node into the database.
            self._write_node_to_db( node_index, node, sim_id )

        # Iterate through the scenario's links.
        for link_index, link in self.sim.links.iterrows():
            link_name = str( 'link' ) + str( link_index )
            # Insert link into the database (stored as port connection).
            self._write_link_to_db( link_name, link, sim_id )

        # Commit session.
        self.commit_citydb_session()


    def _write_simulation_to_db( self, sim_name ):
        # Define function call to insert simulation to database.
        insert_sim = func_insert_simulation( sim_name )

        # Store simulation and retrieve the ID of its database representation.
        sim_query = self.current_session.query( insert_sim ).one()
        sim_id = sim_query[0]

        # Store simulation sequence as JSON-formatted generic string parameter.
        str_sequence = json.dumps( self.sim.sequence, sort_keys = False, separators = ( ',', ': ' ) )
        insert_sequence = func_insert_string_parameter_simulation( sim_id, 'sequence', str_sequence )
        self.current_session.query( insert_sequence ).one()

        # Store simulation time steps as numeric array generic parameter.
        insert_steps = func_insert_array_parameter_simulation( sim_id, 'steps', self.sim.steps, self.sim.time_unit )
        self.current_session.query( insert_steps ).one()

        return sim_id


    def _write_meta_model_to_db( self, meta_name, meta_model ):
        # Define function call to insert meta model to database (stored as template node).
        insert_meta = func_insert_node_template( meta_name )

        # Store meta model and retrieve the ID of its database representation.
        result = self.current_session.query( insert_meta ).one()
        meta_id = result[0]

        for input_attr in meta_model[ 'ToSet' ]:
            # Define function call to insert input attribute to database (stored as input port).
            insert_set_attr = func_insert_port( meta_id, 'input', input_attr[0], input_attr[1] )

            # Store input attribute.
            self.current_session.query( insert_set_attr ).one()

        for output_attr in meta_model[ 'ToGet' ]:
            # Define function call to insert output attribute to database (stored as output port).
            insert_get_attr = func_insert_port( meta_id, 'output', output_attr[0], output_attr[1] )

            # Store output attribute.
            self.current_session.query( insert_get_attr ).one()

        # Collect meta model ID.
        self.meta_model_ids[ meta_name ] = meta_id


    def _retrieve_meta_model_from_db( self, meta_name ):
        meta_model = self.current_session.query( Node ).filter(
            and_(
                Node.name == meta_name,
                Node.is_template == True
            )
        ).one()
        self.meta_model_ids[ meta_name ] = meta_model.id


    def _write_env_to_db( self, env_name, env ):
        # Define function call to insert environment into the database (stored as simulation tool).
        insert_env = func_insert_tool( env_name )

        # Store model and retrieve the ID of its database representation.
        result = self.current_session.query( insert_env ).one()
        env_id = result[0]

        # Store 'Dockerfile' attribute as generic parameter.
        insert_dockerfile_uri = func_insert_uri_parameter_tool(
            env_id, 'dockerfile', pathlib.Path( os.path.abspath( env[ 'Dockerfile' ] ) ).as_uri()
        )
        self.current_session.query( insert_dockerfile_uri ).one()

        # with open( env[ 'Dockerfile' ], 'r' ) as dockerfile:
        #     insert_dockerfile = func_insert_string_parameter_tool( env_id, 'dockerfile', dockerfile.read() )
        #     self.current_session.query( insert_dockerfile ).one()

        # Store 'wrapper' attribute as generic parameter.
        insert_wrapper_uri = func_insert_uri_parameter_tool(
            env_id, 'wrapper', pathlib.Path( os.path.abspath( env[ 'Wrapper' ] ) ).as_uri()
        )
        self.current_session.query( insert_wrapper_uri ).one()

        # with open( env[ 'Wrapper' ], 'r' ) as wrapper:
        #     insert_wrapper = func_insert_string_parameter_tool( env_id, 'wrapper', wrapper.read() )
        #     self.current_session.query( insert_wrapper ).one()

        # Collect model ID.
        self.env_ids[ env_name ] = env_id


    def _retrieve_env_from_db( self, env_name ):
        env = self.current_session.query( SimulationTool ).filter_by( name = env_name ).one()
        self.env_ids[ env_name ] = env.id


    def _write_node_to_db( self, node_name, node, sim_id ):
        # Retrieve meta model ID.
        meta_name = node[ 'Meta' ]
        meta_id = self.meta_model_ids[ meta_name ]

        # Retrieve environment ID.
        env_name = node[ 'Env' ]
        env_id = self.env_ids[ env_name ]

        # Define function call to insert node to database.
        insert_node = func_insert_node( node_name, sim_id, env_id, meta_id )

        # Store node and retrieve the ID of its database representation.
        result = self.current_session.query( insert_node ).one()
        node_id = result[0]

        # Store 'Local' attribute as generic parameter.
        insert_is_local = func_insert_string_parameter_node( node_id,
            'Local', str( node[ 'Local' ] ) )
        self.current_session.query( insert_is_local ).one()

        # Store initial values ('InitVal' attribute) as generic
        # parameters (with attribute 'is_init_parameter' set to true).
        self._write_node_init_vals_to_db( node_id, node[ 'InitVal' ] )

        # Store parameters ('Parameters' attribute) as generic parameters.
        self._write_node_init_vals_to_db( node_id, node[ 'Parameters' ] )

        # Store additional input files ('Files' attribute) to database.
        self._write_node_files_to_db( node_id, node[ 'Files' ] )

        input_ids = {}
        output_ids = {}

        for input_attr in node[ 'ToSet' ]:
            # Define function call to insert input attribute to database (stored as input port).
            insert_port = func_insert_port( node_id, 'input', input_attr[0], input_attr[1] )

            # Store port and retrieve the ID of its database representation.
            result = self.current_session.query( insert_port ).one()
            input_id = result[0]

            # Save the ID (may be needed when saving links).
            input_ids[ input_attr[0] ] = input_id

        for output_attr in node[ 'ToGet' ]:
            # Define function call to insert output attribute to database (stored as output port).
            insert_port = func_insert_port( node_id, 'output', output_attr[0], output_attr[1] )

            # Store port and retrieve the ID of its database representation.
            result = self.current_session.query( insert_port ).one()
            output_id = result[0]

            # Save the ID (may be needed when saving links).
            output_ids[ output_attr[0] ] = output_id

        # Collect data about all input/output IDs for this node.
        self.attribute_ids[ node_name ] = { 'inputs' : input_ids, 'outputs' : output_ids }


    def _write_node_init_vals_to_db( self, node_id, init_vals ):
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
            elif isinstance( value, AssociateCityDBObject ):
                func_insert_init_val = func_insert_object_ref_init_val_node( node_id, name,
                    value.table_name, value.object_id, value.column_name )
            elif isinstance( value, AssociateCityDBGenericAttribute ):
                func_insert_init_val = func_insert_generic_attr_ref_init_val_node( node_id, name,
                    value.attribute_name, value.attribute_id )
            else:
                func_insert_init_val = func_insert_string_init_val_node( node_id, name, str( value ) )

            self.current_session.query( func_insert_init_val ).one()


    def _write_node_params_to_db( self, node_id, params ):
        for name, value in params.items():
            func_insert_param = None

            if isinstance( value, float ):
                func_insert_param = func_insert_real_parameter_node( node_id, name, value )
            elif isinstance( value, int ):
                func_insert_param = func_insert_integer_parameter_node( node_id, name, value )
            elif isinstance( value, str ):
                func_insert_param = func_insert_string_parameter_node( node_id, name, value )
            elif isinstance( value, bool ):
                func_insert_param = func_insert_string_parameter_node( node_id, name, str( value ) )

            self.current_session.query( func_insert_param ).one()


    def _write_node_files_to_db( self, node_id, file_names ):
        for extra_file_name in file_names:
            insert_extra_file_uri = func_insert_uri_parameter_node(
                node_id,
                os.path.basename( extra_file_name ),
                pathlib.Path( os.path.abspath( extra_file_name ) ).as_uri()
            )
            self.current_session.query( insert_extra_file_uri ).one()

            # with open( extra_file_name, 'r' ) as extra_file:
            #     db_file_name = os.path.basename( extra_file_name )
            #     insert_extra_file = func_insert_string_parameter_node( node_id, db_file_name, extra_file.read(),
            #                                                            description = 'file' )
            #     self.current_session.query( insert_extra_file ).one()


    def _write_link_to_db( self, link_name, link, sim_id ):
        # Retrieve information about the link's output attribute.
        get_node_name = link[ 'GetNode' ]
        get_attribute_name = link[ 'GetAttr' ]
        get_attribute_id = self.attribute_ids[ get_node_name ][ 'outputs' ][ get_attribute_name ]

        # Retrieve information about the link's input attribute.
        set_node_name = link[ 'SetNode' ]
        set_attribute_name = link[ 'SetAttr' ]
        set_attribute_id = self.attribute_ids[ set_node_name ][ 'inputs' ][ set_attribute_name ]

        # Define function call to insert link to database (stored as port connection).
        insert_link = func_insert_port_connection( sim_id, link_name, get_attribute_id, set_attribute_id )

        # Store link and retrieve the ID of its database representation.
        result = self.current_session.query( insert_link ).one()
        link_id = result[0]


    # def _write_file_path_as_uri_to_db( self, node_id, file_names ):
    #     for extra_file_name in file_names:
    #         with open( extra_file_name, 'r' ) as extra_file:
    #             db_file_name = os.path.basename( extra_file_name )
    #             insert_extra_file = func_insert_string_parameter_node( node_id, db_file_name, extra_file.read(),
    #                                                                    description = 'file' )
    #             self.current_session.query( insert_extra_file ).one()
