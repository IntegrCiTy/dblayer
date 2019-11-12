from dblayer.access import *
from dblayer.func.func_simpkg import *

import ictdeploy

import decimal
#import pandas
import json


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
        self.sim = ictdeploy.Simulator()

        # Retrieve data from database.
        self._retrieve_simulation_from_db( sim_name )
        self._retrieve_nodes_from_db()
        self._retrieve_model_and_meta_models_from_db()
        self._retrieve_links_from_db()

        # Create simulation setup.
        self._add_meta_models()
        self._add_models()
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
        self.node_parameters = {}
        self.node_init_values = {}
        self.models = {}
        self.model_parameters = {}
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
        self.nodes = dict( [ ( n.name, n ) for n in nodes ] )

        for node_name, node in self.nodes.items():
            # Retrieve generic parameters assciated to node.
            parameters = self.current_session.query( GenericParameterNode ).filter(
                and_(
                    GenericParameterNode.node_id == node.id,
                    GenericParameterNode.is_init_parameter == False
                )
            ).all()
            self.node_parameters[ node.name ] = self._retrieve_generic_parameters( parameters )

            # Retrieve initial values assciated to node.
            init_values = self.current_session.query( GenericParameterNode ).filter(
                and_(
                    GenericParameterNode.node_id == node.id,
                    GenericParameterNode.is_init_parameter == True
                )
            ).all()
            self.node_init_values[ node.name ] = self._retrieve_generic_parameters( init_values )


    def _retrieve_model_and_meta_models_from_db( self ):
        for node_name, node in self.nodes.items():
            # Retrieve model associated to node (stored as SimulationTool).
            model_id = node.tool_id
            model = self.current_session.query( SimulationTool ).filter_by( id = model_id ).one()

            # Store model name in node object.
            node.model = model.name

            # Check if model has been retrieved before.
            if model.name not in self.models:
                self.models[ model.name ] = model

                # Retrieve model parameters
                parameters = self.current_session.query( GenericParameterTool ).filter_by( tool_id = model_id ).all()
                self.model_parameters[ model.name ] = self._retrieve_generic_parameters( parameters )

                # Get associated meta model name.
                meta_model_name = self.model_parameters[ model.name ][ 'meta' ]

                # Check if meta model has been retrieved before.
                if meta_model_name not in self.meta_models:
                    # Retrieve meta model.
                    meta_model = self.current_session.query( Node ).filter(
                        and_(
                            Node.name == meta_model_name,
                            Node.is_template == True
                        )
                    ).one()

                    # Retrieve attributes (inputs/outputs) of meta model.
                    attributes = self.current_session.query( Port ).filter_by( node_id = meta_model.id ).all()

                    self.meta_models[ meta_model_name ] = meta_model
                    self.meta_model_attributes[ meta_model_name ] = attributes


    def _retrieve_links_from_db( self ):
        links = self.current_session.query( PortConnectionExt ).filter_by( simulation_id = self.sim_id ).all()
        self.links = dict( [ ( l.name, l ) for l in links ] )


    def _add_meta_models( self ):
        for meta_model_name, meta_model in self.meta_models.items():
            # Retrieve inputs and outputs of meta model.
            inputs = []
            outputs = []
            for attribute in self.meta_model_attributes[ meta_model_name ]:
                inputs.append( attribute.name ) if ( attribute.type == 'input' ) else outputs.append( attribute.name )

            # Add meta model to simulator.
            self.sim.edit.add_meta(
                name = meta_model_name,
                set_attrs = inputs,
                get_attrs = outputs )


    def _add_models( self ):
        for model_name, model in self.models.items():
            # Retrieve model parameters.
            parameters = self.model_parameters[ model_name ]

            # Special case: check if generic parameter related to 'command' exists.
            command = parameters[ 'command' ] if ( 'command' in parameters ) else None

            # Special case: parse JSON string with list of files.
            files = json.loads( parameters[ 'files' ] ) if ( 'files' in parameters ) else None

            # Add model to simulator.
            self.sim.edit.add_model(
                name = model_name,
                meta = parameters[ 'meta' ],
                image = parameters[ 'image' ],
                wrapper = parameters[ 'wrapper' ],
                command = command,
                files = files )


    def _add_nodes( self ):
        for node_name, node in self.nodes.items():
            # Retrieve node parameters.
            parameters = self.node_parameters[ node_name ]
            str_is_first = parameters[ 'is_first' ] if ( 'is_first' in parameters ) else False

            # Add node to simulator.
            self.sim.edit.add_node(
                name = node_name,
                model = node.model,
                init_values = self.node_init_values[ node_name ],
                is_first = True if ( str_is_first == 'True' ) else False )


    def _add_links( self ):
        for link_name, link in self.links.items():
            # Parse link information.
            get_node_name = link.n1_name if link.p1_type == 'output' else link.n2_name
            get_attribute_name = link.p1_variable_name if link.p1_type == 'output' else link.p2_variable_name
            set_node_name = link.n1_name if link.p1_type == 'input' else link.n2_name
            set_attribute_name = link.p1_variable_name if link.p1_type == 'input' else link.p2_variable_name

            # Add link to simulator.
            self.sim.edit.add_link(
                get_node = get_node_name,
                get_attr = get_attribute_name,
                set_node = set_node_name,
                set_attr = set_attribute_name )


    def _add_sequence( self ):
        groups = []
        for group in json.loads( self.simulation_parameters[ 'sequence' ] ):
            groups.append( self.sim.create_group( *group ) )

        # Create simulation sequence.
        self.sim.create_sequence( *groups )


    def _add_steps( self ):
        self.sim.create_steps( self.simulation_parameters[ 'steps' ] )


    def _retrieve_generic_parameters( self, generic_param_data ):
        # Create dict of parameters.
        generic_param = {}

        # Check which field of the data is present and fill the dict accordingly.
        for data in generic_param_data:
            if data.strval is not None:
                generic_param[data.name] = data.strval
            elif data.intval is not None:
                generic_param[data.name] = data.intval
            elif data.realval is not None:
                generic_param[data.name] = data.realval
            elif data.arrayval is not None:
                generic_param[data.name] = data.arrayval
            elif data.urival is not None:
                generic_param[data.name] = data.urival
            elif data.dateval is not None:
                generic_param[data.name] = data.dateval
            elif data.citydb_table_name is not None:
                generic_param[data.name] = self._retrieve_object_ref( data.citydb_table_name,
                    data.citydb_object_id, data.citydb_column_name )
            elif data.citydb_genericattrib_name is not None:
                generic_param[data.name] = self._retrieve_generic_attr_ref( data.citydb_genericattrib_name,
                    data.citydb_object_id )

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
            return data.strval
        elif attribute.intval is not None:
            return attribute.intval
        elif attribute.realval is not None:
            return attribute.realval
        elif attribute.arrayval is not None:
            return attribute.arrayval
        elif attribute.urival is not None:
            return attribute.urival
        elif attribute.dateval is not None:
            return attribute.dateval
