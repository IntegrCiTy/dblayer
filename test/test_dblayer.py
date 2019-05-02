import pytest

import os
import sqlalchemy.orm.exc

from dblayer import *
from dblayer.func.func_citydb_view import *
from dblayer.func.func_citydb_view_nrg import *
from dblayer.func.func_postgis_geom import *
from dblayer.helpers.utn.electrical_network import *
from dblayer.sim.pandapower import *

import ictdeploy

import pandas as pd
import networkx as nx


@pytest.fixture()
def fix_connect():
    '''
    Fixture for testing. Returns the connection parameters for the database.

    :return: PostgreSQL database connection parameters (dblayer.db.PostgreSQLConnectionInfo)
    '''
    # Define connection parameters.
    return PostgreSQLConnectionInfo(
        user = 'postgres',
        pwd = 'postgres',
        host = 'localhost',
        port = '5432',
        dbname = 'testdb'
    )


@pytest.fixture()
def fix_access( fix_connect ):
    '''
    Fixture for testing. Provides access to the database.

    :return: object for accessing the database (dblayer.Access)
    '''
    # Access the database.
    access = DBAccess()

    # Connect to database and retrieve engine, session and metadata.
    access.connect_to_citydb( fix_connect  )

    return access


@pytest.fixture()
def fix_create_sim():
    '''
    Fixture for testing. Creates a simple ready-to-run co-simulation setup.

    :return: simulation setup with meta, models, nodes, links, groups, sequence and steps implemented (ictdeploy.Simulator)
    '''
    # Create simulation setup.
    sim = ictdeploy.Simulator()

    # Add meta model.
    sim.edit.add_meta(
        name = 'BaseMeta',
        set_attrs = [ 'a' ],
        get_attrs = [ 'b' ]
    )

    # Add model based on meta model.
    sim.edit.add_model(
        name = 'BaseModel',
        meta = 'BaseMeta',
        image = 'integrcity/ict-simple',
        wrapper = os.path.join( 'tests', 'wrappers', 'base_wrap.py' ),
        command = None,
        files = [ os.path.join( 'tests', 'files_to_add', 'empty_file_for_testing_purpose.txt' ) ]
    )

    # Add node based on model.
    sim.edit.add_node(
        name = 'Base0',
        model = 'BaseModel',
        init_values = { 'c': 0.5 },
        is_first = True
    )

    # Add another node based on model.
    sim.edit.add_node(
        name = 'Base1',
        model = 'BaseModel',
        init_values = { 'c': 0.25 }
    )

    # Define links between nodes.
    sim.edit.add_link( get_node = 'Base0', get_attr = 'b', set_node = 'Base1', set_attr = 'a' )
    sim.edit.add_link( get_node = 'Base1', get_attr = 'b', set_node = 'Base0', set_attr = 'a' )

    # Define simulation groups and sequence.
    grp0 = sim.create_group( 'Base0' )
    grp1 = sim.create_group( 'Base1' )
    sim.create_sequence( grp0, grp1 )

    # Define simulation time steps.
    sim.create_steps( [60] * 10 )

    return sim


@pytest.fixture()
def fix_network_id():
    return 1000


def test_cleanup_citydb_schema( fix_access ):
    fix_access.cleanup_citydb_schema()


def test_cleanup_simpkg_schema( fix_access ):
    fix_access.cleanup_simpkg_schema()


def test_map_invalid_class( fix_access ):
    with pytest.raises( RuntimeError ) as e:
        fix_access.map_citydb_object_class( 'UnknownObjectClassName' )
    assert 'RuntimeError: a table name must be specified for user-defined mappings' in str( e )


def test_fill_citydb( fix_access ):
    # Insert new buildings and retrieve their IDs.
    bui_id1 = fix_access.add_citydb_object( insert_building, name = 'BUILDING_01' )
    bui_id2 = fix_access.add_citydb_object( insert_building, name = 'BUILDING_02' )

    # Insert new heat pumps (associated to buildings).
    fix_access.add_citydb_object( insert_heat_pump, name = 'HEATPUMP_01', nom_effcy = 1.2,
        effcy_indicator = 'COP', inst_in_ctyobj_id = bui_id1 )
    fix_access.add_citydb_object( insert_heat_pump, name = 'HEATPUMP_02', nom_effcy = 3.4,
        effcy_indicator = 'COP', inst_in_ctyobj_id = bui_id2 )

    # Insert new time series and retrieve their IDs.
    ts_id1 = fix_access.add_citydb_object( insert_regular_time_series, name = 'TS_DEMAND_01',
        values_array = [ 1, 2, 3 ], values_unit = 'kW', time_interval = 0.25, time_interval_unit = 'h' )
    ts_id2 = fix_access.add_citydb_object( insert_regular_time_series, name = 'TS_DEMAND_02',
        values_array = [ 4, 5, 6 ], values_unit = 'kW', time_interval = 0.25, time_interval_unit = 'h' )

    # Insert new energy demands (associated to time series).
    fix_access.add_citydb_object( insert_energy_demand, name = 'DEMAND_01',
        time_series_id = ts_id1, cityobject_id = bui_id1 )
    fix_access.add_citydb_object( insert_energy_demand, name = 'DEMAND_02',
        time_series_id = ts_id2, cityobject_id = bui_id2 )

    # Insert new generic attributes (associated to buildings).
    fix_access.add_citydb_object( insert_genericattrib_real, attrname = 'BUILDING_01_ATTR_01',
        attrvalue = 0.1, cityobject_id = bui_id1 )
    fix_access.add_citydb_object( insert_genericattrib_integer, attrname = 'BUILDING_01_ATTR_02',
        attrvalue = 2, cityobject_id = bui_id1 )
    fix_access.add_citydb_object( insert_genericattrib_string, attrname = 'BUILDING_01_ATTR_03',
        attrvalue = '3', cityobject_id = bui_id1 )
    fix_access.add_citydb_object( insert_genericattrib_real, attrname = 'BUILDING_02_ATTR_01',
        attrvalue = 4.5, cityobject_id = bui_id2 )
    fix_access.add_citydb_object( insert_genericattrib_integer, attrname = 'BUILDING_02_ATTR_02',
        attrvalue = 6, cityobject_id = bui_id2 )
    fix_access.add_citydb_object( insert_genericattrib_string, attrname = 'BUILDING_02_ATTR_03',
        attrvalue = '7', cityobject_id = bui_id2 )

    fix_access.commit_citydb_session()


def test_read_citydb( fix_access ):
    # Retrieve building data from default 3DCityDB table (citydb.building).
    buildings = fix_access.get_citydb_objects( 'Building' )

    # Expect a query result with two entries.
    assert len( buildings ) == 2

    # Retrieve building data from user-friendly 3DCityDB view (citydb_view.building).
    with pytest.warns( RuntimeWarning ) as record:
        # Retrieve the class mapped to the view.
        Building = fix_access.map_citydb_object_class( 'Building', schema = 'citydb_view' )

        # Use the mapped class to define filter conditions.
        conditions = [ Building.name == 'BUILDING_02' ]

        # Retrieve the data.
        buildings = fix_access.get_citydb_objects( 'Building', conditions = conditions )

        # Expect a query result with only one entry.
        assert len( buildings ) == 1

        # Retrieve the class mapped to the default table.
        GenericAttribute = fix_access.map_citydb_object_class( 'GenericAttribute' )

        # Retrieve all generic attributes associated to a building by joining data from 2 tables.
        attributes = fix_access.join_citydb_objects(
            [ 'GenericAttribute', 'Building' ],
            conditions = [ GenericAttribute.cityobject_id == Building.id ]
            )
        
        assert( len( attributes ) == 6 )

    # Check that only one warning was raised.
    assert len( record ) == 1

    # Check that the message matches.
    assert record[0].message.args[0] == 'Class Building has already been mapped from table: building (schema: citydb). It will be re-mapped from table: building (schema: citydb_view).'


def test_read_simpkg_invalid( fix_connect ):
    with pytest.raises( sqlalchemy.orm.exc.NoResultFound ) as e:
        reader = DBReader( fix_connect )
        # Try to read a scenario that does not exist.
        sim = reader.read_from_db( 'TestSimX' )
    assert 'No row was found for one()' in str( e )


def test_write_simpkg( fix_connect, fix_create_sim ):
    writer = DBWriter( fix_connect )
    writer.write_to_db( fix_create_sim, 'TestSim' )

#         # NOT YET IMPLEMENTED: Try to write a scenario with an already existing name to database.
#         try:
#             writer.write_to_db( fix_create_sim, 'TestSim' )
#         except RuntimeError as e:
#             expected_message = ''
#             self.assertEqual( str( e ) )


def test_write_and_read_simpkg( fix_connect, fix_create_sim ):
    # Define simulation setup name.
    sim_name = 'TestSim1'

    # Write simulation setup to database. Do not write meta models and models, because
    # they have already been written to the database in one of the previous tests.
    sim_write = fix_create_sim
    writer = DBWriter( fix_connect )
    writer.write_to_db( sim_write, sim_name, write_meta_models = False, write_models = False )

    # Read simulation setup from database.
    reader = DBReader( fix_connect )
    sim_read = reader.read_from_db( sim_name )

    assert type( sim_read.edit.links ) is pd.DataFrame
    assert type( sim_read.edit.graph ) is nx.MultiDiGraph
    assert len( sim_read.edit.nodes ) == 2
    assert len( sim_read.edit.links ) == 2
    for _, row in  sim_read.edit.nodes.iterrows():
        assert row[ 'model' ] == 'BaseModel'
        assert row[ 'meta' ] == 'BaseMeta'
        assert row[ 'to_set' ] == [ 'a' ]
        assert row[ 'to_get' ] == [ 'b' ]
        assert row[ 'image' ] == 'integrcity/ict-simple'
        assert row[ 'wrapper' ] == os.path.join( 'tests', 'wrappers', 'base_wrap.py' )
        assert row[ 'files' ] == [ os.path.join( 'tests', 'files_to_add', 'empty_file_for_testing_purpose.txt' ) ]
        assert row[ 'command' ] is None
    assert( sim_read.edit.nodes.loc[ 'Base0' ].init_values[ 'c' ] == 0.5 )
    assert( sim_read.edit.nodes.loc[ 'Base1' ].init_values[ 'c' ] == 0.25 )
    g_dict =  sim_read.edit.interaction_graph
    assert len( g_dict[ 'links' ] ) == 2
    assert len( g_dict[ 'nodes' ] ) == 2
    assert  sim_read.steps == [ 60, 60, 60, 60, 60, 60, 60, 60, 60, 60 ]
    assert  sim_read.sequence == [ ( 'Base0', ), ( 'Base1', ) ]


def test_write_and_read_associate_simpkg( fix_connect, fix_access, fix_create_sim ):
    sim_name = 'TestSim2'

    HeatPump = fix_access.map_citydb_object_class( 'HeatPump', schema = 'citydb_view',
        table_name = 'nrg8_conv_system_heat_pump' )
    conditions = [ HeatPump.name == 'HEATPUMP_02', HeatPump.nom_effcy==3.4 ]
    heatpumps = fix_access.get_citydb_objects( 'HeatPump', conditions = conditions )

    assert( len( heatpumps ) == 1 )
    heatpump_id = heatpumps[0].id

    GenericAttribute = fix_access.map_citydb_object_class( 'GenericAttribute' )
    conditions = [ GenericAttribute.attrname == 'BUILDING_02_ATTR_01' ]
    attributes = fix_access.get_citydb_objects( 'GenericAttribute', conditions = conditions )
    attribute_id = attributes[0].id

    associated_sim = fix_create_sim
    associated_sim.edit.nodes.loc[ 'Base0' ].init_values[ 'c' ] = AssociateCityDBObject(
        table_name = 'citydb_view.nrg8_conv_system_heat_pump', object_id = heatpump_id, column_name = 'nom_effcy' )
    associated_sim.edit.nodes.loc[ 'Base1' ].init_values[ 'c' ] = AssociateCityDBGenericAttribute(
        attribute_name = 'BUILDING_02_ATTR_01', attribute_id = attribute_id )

    writer = DBWriter( fix_connect )
    writer.write_to_db( associated_sim, sim_name, write_meta_models = False, write_models = False )

    # Read simulation setup from database.
    reader = DBReader( fix_connect )
    sim_read = reader.read_from_db( sim_name )

    assert( sim_read.edit.nodes.loc[ 'Base0' ].init_values[ 'c' ] == 3.4 )
    assert( sim_read.edit.nodes.loc[ 'Base1' ].init_values[ 'c' ] == 4.5 )


def test_geom_func( fix_connect, fix_access ):
    # Check implementation of function 'geom_from_text'.
    geo = fix_access.execute_function( geom_from_text( 'POINT(1 2)' ) )
    assert( geo == '0101000000000000000000F03F0000000000000040' )
    text = fix_access.execute_function( geom_as_text( geo ) )
    assert( text.upper() == 'POINT(1 2)' )

    # Check implementation of function 'geom_from_2dpoint'.
    geo = fix_access.execute_function( geom_from_2dpoint( Point2D( 3, 5 ) ) )
    assert( geo == '0101000080000000000000084000000000000014400000000000000000' )
    text = fix_access.execute_function( geom_as_text( geo ) )
    print( text.upper() == 'POINT(3 5)' )

    # Check implementation of function 'geom_from_2dlinestring'.
    geo = fix_access.execute_function( geom_from_2dlinestring( [ Point2D( 3, 5 ), Point2D( 4, 6 ) ] ) )
    assert( geo == '010200008002000000000000000000084000000000000014400000000000000000000000000000104000000000000018400000000000000000' )
    text = fix_access.execute_function( geom_as_text( geo ) )
    assert( text.upper() == 'LINESTRING Z (3 5 0,4 6 0)' )

    # Check implementation of function 'geom_from_2dpolygon'.
    geo = fix_access.execute_function( geom_from_2dpolygon( [ Point2D( 3, 5 ), Point2D( 4, 6 ), Point2D( 15, 7 ), Point2D( 3, 5 ) ] ) )
    assert( geo == '010300008001000000040000000000000000000840000000000000144000000000000000000000000000001040000000000000184000000000000000000000000000002E400000000000001C400000000000000000000000000000084000000000000014400000000000000000' )
    text = fix_access.execute_function( geom_as_text( geo ) )
    assert( text.upper() == 'POLYGON Z ((3 5 0,4 6 0,15 7 0,3 5 0))' )

    try:
        # First and last point do not coincide --> will raise error.
        fix_access.execute_function( geom_from_2dpolygon( [ Point2D( 3, 5 ), Point2D( 4, 6 ), Point2D( 15, 7 ) ] ) )
    except ValueError as e:
        assert( str( e ) == 'first and last point do not coincide' )


def test_fill_citydb_utn_electrical( fix_access, fix_network_id ):

    # Define spatial reference ID.
    srid = 25833

    # Create network and network graph.
    ntw_id = fix_access.add_citydb_object( insert_network, name = 'test_network', id = fix_network_id )
    ntw_graph_id = fix_access.add_citydb_object( insert_network_graph, name = 'test_network_graph', network_id = ntw_id )

    # Add electrical busses.
    bus_lv = write_bus_to_db( fix_access, 'bus-lv', 'busbar', Point2D( 2., 0. ), 0.4, srid, ntw_id, ntw_graph_id )
    bus_mv = write_bus_to_db( fix_access, 'bus-mv', 'busbar', Point2D( 1., 0. ), 20., srid, ntw_id, ntw_graph_id )
    bus_1 = write_bus_to_db( fix_access, 'bus-1', 'busbar', Point2D( 3., 0. ), 0.4, srid, ntw_id, ntw_graph_id )
    bus_2 = write_bus_to_db( fix_access, 'bus-2', 'busbar', Point2D( 10., 0. ), 0.4, srid, ntw_id, ntw_graph_id )

    # Add transformer.
    write_transformer_to_db( fix_access, 'trafo', bus_mv, bus_lv, '0.63 MVA 20/0.4 kV', srid, ntw_id, ntw_graph_id )

    # Add external grid.
    write_terminal_element_to_db( fix_access, 'feeder', 'external-grid', bus_mv, srid, ntw_id, ntw_graph_id )

    # Add switch.
    write_switch_to_db( fix_access, 'switch', bus_lv, bus_1, 'CB', srid, ntw_id, ntw_graph_id )

    # Add electrical line.
    write_line_to_db( fix_access, 'line', bus_1, bus_2, 0.01, 0.1, 0.05, 1., 'cs', srid, ntw_id, ntw_graph_id )

    # Add electrical load.
    write_load_to_db( fix_access, 'load', bus_2, 10., 0.1, srid, ntw_id, ntw_graph_id )

    fix_access.commit_citydb_session()


def test_sim_utn_electrical_pandapower( fix_connect, fix_network_id ):

    # Instantiate reader.
    pp_reader = PandaPowerModelDBReader( fix_connect )

    with pytest.warns( RuntimeWarning ) as record:
        # Create simulation model from database.
        net = pp_reader.get_net( network_id = fix_network_id )

    assert( len( record ) == 1 )

    # Check number of elements in the simulation model.
    assert( len( net.bus ) == 4 )
    assert( len( net.load ) == 1 )
    assert( len( net.switch ) == 1 )
    assert( len( net.ext_grid ) == 1 )
    assert( len( net.line ) == 1 )
    assert( len( net.trafo ) == 1 )
    assert( len( net.line_geodata ) == 1 )
    assert( len( net.bus_geodata ) == 4 )

    # Run a power flow calculation.
    pp.runpp( net, numba=False )

    # Check results.
    bus_mv_id = pp.get_element_index( net, 'bus', 'bus-mv' )
    bus_2_id = pp.get_element_index( net, 'bus', 'bus-2' )
    assert( net.res_bus.iloc[bus_mv_id].p_kw == pytest.approx( -11.652311, 1e-4 ) )
    assert( net.res_bus.iloc[bus_mv_id].q_kvar == pytest.approx( -0.111221, 1e-4 ) )
    assert( net.res_bus.iloc[bus_2_id].vm_pu == pytest.approx( 0.999739, 1e-4 ) )
    assert( net.res_bus.iloc[bus_2_id].va_degree == pytest.approx( -0.058996, 1e-4 ) )
    assert( net.res_line.iloc[0].i_ka == pytest.approx( 0.014438, 1e-4 ) )
    assert( net.res_line.iloc[0].loading_percent == pytest.approx( 1.443825, 1e-4 ) )
