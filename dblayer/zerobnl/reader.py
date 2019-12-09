from dblayer.access import *
from dblayer.func.func_simpkg import *

import zerobnl

import decimal
#import pandas
import json

from os.path import abspath, join
import urllib.parse

import warnings


class DBReader( DBAccess ):
    """
    Helper class for reading simulation setups from a database.
    Requires the Simulation Package schema to be installed.
    """

    def __init__( self, connect ):
        """
        Constructor.

        :param connect: tuple containing connection parameters for database (PostgreSQLConnectionInfo)
        """
        super().__init__()
        self._reset()
        self.connect_to_citydb( connect )


    def read_from_db( self, sim_name ):
        """
        Read scenario from database. Requires SimulationPackage schema to be installed. Returns a new schema.

        :param sim_name: name used to identify this simulation setup in the database (str)
        :return; simulation setup (ictdeploy.Simulator)
        """
        # Initialize object relational mapper.
        self._init_simpkg_orm()

        # Reset internal dicts.
        self._reset()

        # Start session.
        if self.current_session is None: self.start_citydb_session()

        # Create simulation setup.
        self.sim = zerobnl.CoSim()

        # Retrieve data from database.
        self._retrieve_simulation_from_db( sim_name )
        self._retrieve_nodes_from_db()
        self._retrieve_envs_and_meta_models_from_db()
        self._retrieve_links_from_db()

        # Create simulation setup.
        self._add_meta_models()
        self._add_envs()
        self._add_nodes()
        self._add_links()
        self._add_sequence()
        self._add_steps()

        # Return the simulation setup.
        return self.sim


    def _reset( self ):
        self.sim = None
        self.sim_id = None
        self.simulation_parameters = {}
        self.nodes = {}
        self.node_init_values = {}
        self.node_parameters = {}
        self.node_file_uris = {}
        self.envs = {}
        self.env_parameters = {}
        self.meta_models = {}
        self.meta_model_attributes = {}


    def _retrieve_simulation_from_db( self, sim_name ):
        # Retrieve the simulation ID.
        sim_query = self.current_session.query( Simulation ).filter_by( name = sim_name ).one()
        self.sim_id = sim_query.id

        # Retrieve generic parameters assciated to simulation.
        parameters = self.current_session.query( GenericParameterSimulation ).filter_by( simulation_id = self.sim_id ).all()
        self.simulation_parameters = self._retrieve_generic_parameters( parameters )


    def _retrieve_nodes_from_db( self ):
        # Retrieve nodes of the simulation configuration.
        nodes = self.current_session.query( Node ).filter(
            and_(
                Node.simulation_id == self.sim_id,
                Node.is_template == False )
            ).all()
        self.nodes = { n.name: n for n in nodes }

        for node_name, node in self.nodes.items():
            # Retrieve generic parameter info assciated to node.
            parameters = self.current_session.query( GenericParameterNode ).filter(
                and_(
                    GenericParameterNode.node_id == node.id,
                    GenericParameterNode.is_init_parameter == False,
                    GenericParameterNode.urival == None
                )
            ).all()
            self.node_parameters[ node.name ] = self._retrieve_generic_parameters( parameters )

            # Retrieve additional file info assciated to node.
            files = self.current_session.query( GenericParameterNode ).filter(
                and_(
                    GenericParameterNode.node_id == node.id,
                    GenericParameterNode.is_init_parameter == False,
                    GenericParameterNode.urival != None
                )
            ).all()
            self.node_file_uris[ node.name ] = self._retrieve_generic_parameters( files )

            # Retrieve initial value info assciated to node.
            init_values = self.current_session.query( GenericParameterNode ).filter(
                and_(
                    GenericParameterNode.node_id == node.id,
                    GenericParameterNode.is_init_parameter == True
                )
            ).all()
            self.node_init_values[ node.name ] = self._retrieve_generic_parameters( init_values )


    def _retrieve_envs_and_meta_models_from_db( self ):
        for node_name, node in self.nodes.items():
            # Retrieve environment associated to node (stored as SimulationTool).
            env_id = node.tool_id
            env = self.current_session.query( SimulationTool ).filter_by( id = env_id ).one()

            # Store environment name in node object.
            node.env = env.name

            # Check if model has been retrieved before.
            if env.name not in self.envs:
                self.envs[ env.name ] = env

                # Retrieve environment parameters
                parameters = self.current_session.query( GenericParameterTool ).filter_by( tool_id = env_id ).all()
                self.env_parameters[ env.name ] = self._retrieve_generic_parameters( parameters )

            # Retrieve meta model associated to node (stored as Node with attribute 'is_template' set to True).
            meta_model_id = node.parent_id
            meta_model = self.current_session.query( Node ).filter(
                Node.id == meta_model_id,
                Node.is_template == True
            ).one()

            # Store meta model name in node object.
            node.meta_model = meta_model.name

            # Check if meta model has been retrieved before.
            if meta_model.name not in self.meta_models:
                self.meta_models[ meta_model.name ] = meta_model

                # Retrieve attributes (inputs/outputs) of meta model.
                attributes = self.current_session.query( Port ).filter_by( node_id = meta_model_id ).all()
                self.meta_model_attributes[ meta_model.name ] = attributes


    def _retrieve_links_from_db( self ):
        links = self.current_session.query( PortConnectionExt ).filter_by( simulation_id = self.sim_id ).all()
        self.links = dict( [ ( l.name, l ) for l in links ] )


    def _add_meta_models( self ):
        for meta_model_name, meta_model in self.meta_models.items():
            # Retrieve inputs and outputs of meta model.
            inputs = []
            outputs = []
            for attr in self.meta_model_attributes[ meta_model_name ]:
                attr_info = ( attr.variable_name, attr.variable_type )
                inputs.append( attr_info ) if ( attr.type == 'input' ) else outputs.append( attr_info )

            # Add meta model to simulator.
            self.sim.create_meta_model(
                meta_model = meta_model_name,
                list_of_attrs_to_set = inputs,
                list_of_attrs_to_get = outputs )


    def _add_envs( self ):
        for env_name, env in self.envs.items():
            # Retrieve model parameters.
            parameters = self.env_parameters[ env_name ]

            dockerfile_uri = parameters[ 'dockerfile' ]
            dockerfile_uri_parsed = urllib.parse.urlparse( dockerfile_uri )
            dockerfile_filename = abspath( join( dockerfile_uri_parsed.netloc, dockerfile_uri_parsed.path ) )
            if not os.path.isfile( dockerfile_filename ):
                warnings.warn( 'file not found: {}'.format( dockerfile_filename ), RuntimeWarning )

            # # Create Dockerfile from database
            # dockerfile_data = parameters[ 'dockerfile' ]
            # dockerfile_filename = '{}_dockerfile'.format( env_name )
            # if not isinstance( dockerfile_data, str ):
            #     raise RuntimeError( 'No Dockerfile found for environment \'{}\''.format( env_name ) )
            # else:
            #     with open( dockerfile_filename, 'w' ) as dockerfile:
            #         dockerfile.write( dockerfile_data )

            wrapper_uri = parameters[ 'wrapper' ]
            wrapper_uri_parsed = urllib.parse.urlparse( wrapper_uri )
            wrapper_filename = abspath( join( wrapper_uri_parsed.netloc, wrapper_uri_parsed.path ) )
            if not os.path.isfile( wrapper_filename ):
                warnings.warn( 'file not found: {}'.format( wrapper_filename ), RuntimeWarning )

            # # Create Dockerfile from database
            # wrapper_data = parameters[ 'wrapper' ]
            # wrapper_filename = '{}_wrapper.py'.format( env_name )
            # if not isinstance( wrapper_data, str ):
            #     raise RuntimeError( 'No wrapper found for environment \'{}\''.format( env_name ) )
            # else:
            #     with open( wrapper_filename, 'w' ) as wrapper:
            #         wrapper.write( wrapper_data )

            # Add model to simulator.
            self.sim.create_environment(
                env = env_name,
                wrapper = wrapper_filename,
                dockerfile = dockerfile_filename
            )


    def _add_nodes( self ):
        for node_name, node in self.nodes.items():
            # Retrieve node parameters.
            parameters = dict( self.node_parameters[ node_name ] )

            # If available, extract parameter 'Local' to separate variable and remove from dict of parameters.
            local = False
            if 'Local' in parameters:
                local = True if ( parameters[ 'Local' ] == 'True' ) else False
                del parameters[ 'Local' ]

            # Retrieve initial values.
            init_values = self.node_init_values[ node_name ]

            # Retrieve paths to extra files.
            files = []
            for _, uri in self.node_file_uris[ node_name ].items():
                uri_parsed = urllib.parse.urlparse( uri )
                filepath = abspath( join( uri_parsed.netloc, uri_parsed.path ) )

                if not os.path.isfile( filepath ):
                    warnings.warn( 'file not found: {}'.format( filepath ), RuntimeWarning )

                files.append( filepath )

            # Add node to simulator.
            self.sim.add_node(
                node = node_name,
                meta = node.meta_model,
                env = node.env,
                init_values = init_values,
                parameters = parameters,
                files = files,
                local = local
            )


    def _add_links( self ):
        for link_name, link in self.links.items():
            # Parse link information.
            get_node_name = link.n1_name if link.p1_type == 'output' else link.n2_name
            get_attribute_name = link.p1_variable_name if link.p1_type == 'output' else link.p2_variable_name
            set_node_name = link.n1_name if link.p1_type == 'input' else link.n2_name
            set_attribute_name = link.p1_variable_name if link.p1_type == 'input' else link.p2_variable_name

            # Add link to simulator.
            self.sim.add_link(
                get_node = get_node_name,
                get_attr = get_attribute_name,
                set_node = set_node_name,
                set_attr = set_attribute_name
            )


    def _add_sequence( self ):
        # Parse sequence from JSON string (stored as generic parameter).
        sequence = json.loads( self.simulation_parameters[ 'sequence' ] )

        # Create simulation sequence.
        self.sim.create_sequence( sequence )


    def _add_steps( self ):
        steps = self.simulation_parameters[ 'steps' ]
        self.sim.create_steps( steps[0] )
        self.sim.set_time_unit( steps[1] )


    def _retrieve_generic_parameters( self, generic_param_data ):
        # Create dict of parameters.
        generic_param = {}

        # Check which field of the data is present and fill the dict accordingly.
        for data in generic_param_data:
            if data.strval is not None:
                value = data.strval
            elif data.intval is not None:
                value = data.intval
            elif data.realval is not None:
                value = float( data.realval )
            elif data.arrayval is not None:
                value = [ float(x) for x in data.arrayval ]
            elif data.urival is not None:
                value = data.urival
            elif data.dateval is not None:
                value = data.dateval
            elif data.citydb_table_name is not None:
                value = self._retrieve_object_ref( data.citydb_table_name,
                    data.citydb_object_id, data.citydb_column_name )
            elif data.citydb_genericattrib_name is not None:
                value = self._retrieve_generic_attr_ref( data.citydb_genericattrib_name,
                    data.citydb_object_id )

            if data.unit == None:
                generic_param[data.name] = value
            else:
                generic_param[data.name] = ( value, data.unit )

        # Return dict.
        return generic_param


    def _retrieve_object_ref( self, table_name, object_id, column_name ):
        # Retrieve meta data.
        metadata = MetaData( self.engine )

        # Extract name of actual schema and table.
        schema_name, table_name = table_name.split( '.' )

        # Define table.
        table = None
        with warnings.catch_warnings():
            warnings.simplefilter( 'ignore', category = sa_exc.SAWarning )

            if schema_name is 'citydb_view':
                table = Table( table_name, metadata, Column( 'id', Integer, primary_key = True ),
                    autoload = True, schema = schema_name )
            else:
                table = Table( table_name, metadata,
                    autoload = True, schema = schema_name )

        # Construct SQL command using SQLAlchemy.
        sql_command = select( [ getattr( table.c, column_name ) ] ).where( table.c.id == object_id )

        # Connect to database and retrieve result.
        connection = self.engine.connect()
        result = connection.execute( sql_command ).scalar()

        if isinstance( result, decimal.Decimal ):
            return float( result )

        return result



    def _retrieve_generic_attr_ref( self, generic_attr_name, generic_attr_id ):
        # Retrieve generic attribute from database.
        attribute = self.current_session.query( GenericAttribute ).filter(
            and_(
                GenericAttribute.attrname == generic_attr_name,
                GenericAttribute.id == generic_attr_id
            )
        ).one()

        # Return value.
        if attribute.strval is not None:
            data = attribute.strval
        elif attribute.intval is not None:
            data = attribute.intval
        elif attribute.realval is not None:
            data = attribute.realval
        elif attribute.arrayval is not None:
            data = attribute.arrayval
        elif attribute.urival is not None:
            data = attribute.urival
        elif attribute.dateval is not None:
            data = attribute.dateval

        if attribute.unit != None:
            return ( data, attribute.unit )
        else:
            return data
