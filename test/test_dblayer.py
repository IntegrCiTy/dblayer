import pytest

import os
import sqlalchemy.orm.exc

from dblayer import *
from dblayer.func.func_citydb_pkg import *
from dblayer.func.func_citydb_view import *
from dblayer.func.func_citydb_view_nrg import *
from dblayer.func.func_postgis_geom import *

from dblayer.sim.pandapower import *
from dblayer.sim.pandathermal import *
from dblayer.sim.pandangas import *

import dblayer.helpers.utn.electrical_network as el_net
import dblayer.helpers.utn.thermal_network as th_net
import dblayer.helpers.utn.gas_network as gas_net

from dblayer.zerobnl.reader import *
from dblayer.zerobnl.writer import *

import pandangas.simulation as gas_sim

import pandas as pd
import networkx as nx

import zerobnl


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
        dbname = 'citydb'
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
def fix_dockerfile():
    '''
    Specify name of dummy Dockerfile.
    '''
    return 'Dockerfile_base'


@pytest.fixture()
def fix_wrapper():
    '''
    Specify name of dummy wrapper.
    '''
    return 'wrapper_base.py'


@pytest.fixture()
def fix_create_sim( fix_dockerfile, fix_wrapper ):
    '''
    Fixture for testing. Creates a simple ready-to-run co-simulation setup.

    :return: simulation setup with meta, envs, nodes, links, sequence and steps implemented (zerobnl.CoSim)
    '''
    # Create simulation setup.
    sim = zerobnl.CoSim()

    # Add meta model.
    sim.create_meta_model(
        meta_model = 'MetaBase',
        list_of_attrs_to_set = [ ( 'a', 'unit' ) ],
        list_of_attrs_to_get = [ ( 'b', 'unit' ) ]
    )

    # Add environment for instances of the meta model.
    sim.create_environment(
        env = 'EnvBase',
        wrapper = os.path.join( os.path.dirname( __file__ ), 'data', fix_wrapper ),
        dockerfile = os.path.join( os.path.dirname( __file__ ), 'data', fix_dockerfile )
    )

    # Add node based on meta model and environment.
    sim.add_node(
        node = 'Base0',
        meta = 'MetaBase',
        env = 'EnvBase',
        init_values = { 'c': .5 },
        files = [ os.path.join( os.path.dirname( __file__ ), 'data', 'dummy_file.txt' ) ]
    )

    # Add another node based on meta model and environment.
    sim.add_node(
        node = 'Base1',
        meta = 'MetaBase',
        env = 'EnvBase',
        init_values = { 'c': .25 }
    )

    # Define links between nodes.
    sim.add_link( get_node = 'Base0', get_attr = 'b', set_node = 'Base1', set_attr = 'a' )
    sim.add_link( get_node = 'Base1', get_attr = 'b', set_node = 'Base0', set_attr = 'a' )

    # Define simulation groups and sequence.
    sim.create_sequence( [ [ 'Base0' ], [ 'Base1' ] ] )

    # Define simulation time steps.
    sim.set_time_unit( 'seconds' )
    sim.create_steps( [15] * 4 * 60 )

    return sim


@pytest.fixture()
def fix_electrical_network_id():
    return 1000


@pytest.fixture()
def fix_thermal_network_id():
    return 2000


@pytest.fixture()
def fix_gas_network_id():
    return 3000


@pytest.fixture()
def fix_srid():
    return 4326

def test_cleanup_citydb_schema( fix_access ):
    fix_access.cleanup_citydb_schema()


def test_cleanup_simpkg_schema( fix_access ):
    fix_access.cleanup_simpkg_schema()


def test_map_invalid_class( fix_access ):
    with pytest.raises( RuntimeError ) as e:
        fix_access.map_citydb_object_class( 'UnknownObjectClassName' )
    assert 0 != len( str( e ) )


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
    assert '<ExceptionInfo NoResultFound tblen=4>' == str( e )


def test_write_simpkg( fix_connect, fix_create_sim ):
    writer = DBWriter( fix_connect )
    writer.write_to_db( fix_create_sim, 'TestSim' )

#         # NOT YET IMPLEMENTED: Try to write a scenario with an already existing name to database.
#         try:
#             writer.write_to_db( fix_create_sim, 'TestSim' )
#         except RuntimeError as e:
#             expected_message = ''
#             self.assertEqual( str( e ) )


def test_write_and_read_simpkg( fix_connect, fix_create_sim, fix_dockerfile, fix_wrapper ):
    # Define simulation setup name.
    sim_name = 'TestSim1'

    # Write simulation setup to database. Do not write meta models and models, because
    # they have already been written to the database in one of the previous tests.
    sim_write = fix_create_sim
    writer = DBWriter( fix_connect )
    writer.write_to_db( sim_write, sim_name, write_meta_models = False, write_envs = False )

    # Read simulation setup from database.
    reader = DBReader( fix_connect )
    sim_read = reader.read_from_db( sim_name )

    assert type( sim_read.nodes ) is pd.DataFrame
    assert type( sim_read.links ) is pd.DataFrame
    assert len( sim_read.nodes ) == 2
    assert len( sim_read.links ) == 2
    for _, row in  sim_read.nodes.iterrows():
        assert row[ 'Env' ] == 'EnvBase'
        assert row[ 'Meta' ] == 'MetaBase'
        assert row[ 'ToSet' ] == [ ( 'a', 'unit' ) ]
        assert row[ 'ToGet' ] == [ ( 'b', 'unit' ) ]
        assert row[ 'Dockerfile' ] == os.path.join( os.path.dirname( __file__ ), 'data', fix_dockerfile )
        assert row[ 'Wrapper' ] == os.path.join( os.path.dirname( __file__ ), 'data', fix_wrapper )
        assert row[ 'Local' ] == False
        assert row[ 'Parameters' ] == {}
    assert sim_read.nodes.loc[ 'Base0' ].InitVal[ 'c' ] == 0.5
    assert sim_read.nodes.loc[ 'Base1' ].InitVal[ 'c' ] == 0.25
    assert sim_read.nodes.loc[ 'Base0' ].Files == [ os.path.join( os.path.dirname( __file__ ), 'data', 'dummy_file.txt' ) ]
    assert sim_read.nodes.loc[ 'Base1' ].Files == []
    assert  sim_read.steps == [15] * 4 * 60
    assert  sim_read.sequence == [ [ 'Base0' ], [ 'Base1' ] ]


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
    associated_sim.nodes.loc[ 'Base0' ].InitVal[ 'c' ] = AssociateCityDBObject(
        table_name = 'citydb_view.nrg8_conv_system_heat_pump', object_id = heatpump_id, column_name = 'nom_effcy' )
    associated_sim.nodes.loc[ 'Base1' ].InitVal[ 'c' ] = AssociateCityDBGenericAttribute(
        attribute_name = 'BUILDING_02_ATTR_01', attribute_id = attribute_id )

    writer = DBWriter( fix_connect )
    writer.write_to_db( associated_sim, sim_name, write_meta_models = False, write_envs = False )

    # Read simulation setup from database.
    reader = DBReader( fix_connect )
    sim_read = reader.read_from_db( sim_name )

    assert( sim_read.nodes.loc[ 'Base0' ].InitVal[ 'c' ] == 3.4 )
    assert( sim_read.nodes.loc[ 'Base1' ].InitVal[ 'c' ] == 4.5 )


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


def test_insert_surface_geometry( fix_access, fix_srid ):

    geom_2d_points = [ Point2D( 0., 0. ), Point2D( 0., 1. ), Point2D( 1., 1. ), Point2D( 0., 0. ) ]

    geom = fix_access.execute_function(
        geom_from_2dpolygon( geom_2d_points, fix_srid )
        )

    geom_id = fix_access.add_citydb_object(
        insert_surface_geometry,
        geometry = geom
        )


def test_fill_citydb_utn_electrical( fix_access, fix_electrical_network_id, fix_srid ):

    # Define spatial reference ID.
    srid = fix_srid

    # Create network and network graph.
    ( ntw_id, ntw_graph_id ) = el_net.write_network_to_db(
        fix_access,
        name = 'test_electrical_network',
        type = 'singlePhaseAlternatingCurrent',
        id = fix_electrical_network_id
        )

    # Add electrical busses.
    bus_lv = el_net.write_bus_to_db( fix_access, 'bus-lv', 'busbar', Point2D( 2., 0. ), 0.4, srid, ntw_id, ntw_graph_id )
    bus_mv = el_net.write_bus_to_db( fix_access, 'bus-mv', 'busbar', Point2D( 1., 0. ), 20., srid, ntw_id, ntw_graph_id )
    bus_1 = el_net.write_bus_to_db( fix_access, 'bus-1', 'busbar', Point2D( 3., 0. ), 0.4, srid, ntw_id, ntw_graph_id )
    bus_2 = el_net.write_bus_to_db( fix_access, 'bus-2', 'busbar', Point2D( 10., 0. ), 0.4, srid, ntw_id, ntw_graph_id )

    # Add transformer.
    el_net.write_transformer_to_db( fix_access, 'trafo', bus_mv, bus_lv, '0.63 MVA 20/0.4 kV', srid, ntw_id, ntw_graph_id )

    # Add external grid.
    el_net.write_terminal_element_to_db( fix_access, 'feeder', 'external-grid', bus_mv, srid, ntw_id, ntw_graph_id )

    # Add switch.
    el_net.write_switch_to_db( fix_access, 'switch', bus_lv, bus_1, 'CB', srid, ntw_id, ntw_graph_id )

    # Add electrical line.
    el_net.write_line_to_db( fix_access, 'line', bus_1, bus_2, 0.01, 0.1, 0.05, 1., 'cable', srid, ntw_id, ntw_graph_id )

    # Add electrical load.
    el_net.write_load_to_db( fix_access, 'load', bus_2, 10., 0.1, srid, ntw_id, ntw_graph_id )

    fix_access.commit_citydb_session()


def test_sim_utn_electrical_pandapower( fix_connect, fix_electrical_network_id ):

    # Instantiate reader.
    pp_reader = PandaPowerModelDBReader( fix_connect )

    with pytest.warns( RuntimeWarning ) as record:
        # Create simulation model from database.
        net = pp_reader.get_net( network_id = fix_electrical_network_id )

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


def test_fill_citydb_utn_thermal( fix_access, fix_thermal_network_id, fix_srid ):

    # Define spatial reference ID.
    srid = fix_srid

    # Create network and network graph.
    ( ntw_id, ntw_graph_id ) = th_net.write_network_to_db(
        fix_access,
        name = 'test_thermal_network',
        id = fix_thermal_network_id
        )

    # Dict for most relevant data of thermal nodes.
    nodes_data = {}

    # Add thermal source.
    nodes_data['SRCE'] = th_net.write_terminal_element_to_db( fix_access, 'SRCE', Point2D( 0., 0. ), 'thermal-source', srid, ntw_id, ntw_graph_id )

    # Add thermal sinks.
    nodes_data['SNK1'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK1', Point2D( 10, 10 ), 10., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK2'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK2', Point2D( 20, 10 ), 20., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK3'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK3', Point2D( 30, 10 ), 10., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK4'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK4', Point2D( 25, -10 ), 50., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK5'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK5', Point2D( 35, -10 ), 10., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK6'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK6', Point2D( 40, 10 ), 20., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK7'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK7', Point2D( 50, 10 ), 10., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK8'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK8', Point2D( 60, 10 ), 30., 'kW', srid, ntw_id, ntw_graph_id )
    nodes_data['SNK9'] = th_net.write_dhw_sink_to_db( fix_access, 'SNK9', Point2D( 70, 10 ), 10., 'kW', srid, ntw_id, ntw_graph_id )

    # Add pipe junctions.
    nodes_data['N0'] = th_net.write_junction_to_db( fix_access, 'N0', Point2D( 10, 0 ), srid, ntw_id, ntw_graph_id )
    nodes_data['N1'] = th_net.write_junction_to_db( fix_access, 'N1', Point2D( 20, 0 ), srid, ntw_id, ntw_graph_id )
    nodes_data['N2'] = th_net.write_junction_to_db( fix_access, 'N2', Point2D( 30, 0 ), srid, ntw_id, ntw_graph_id )
    nodes_data['N3'] = th_net.write_junction_to_db( fix_access, 'N3', Point2D( 40, 0 ), srid, ntw_id, ntw_graph_id )
    nodes_data['N4'] = th_net.write_junction_to_db( fix_access, 'N4', Point2D( 50, 0 ), srid, ntw_id, ntw_graph_id )
    nodes_data['N5'] = th_net.write_junction_to_db( fix_access, 'N5', Point2D( 60, 0 ), srid, ntw_id, ntw_graph_id )
    nodes_data['N6'] = th_net.write_junction_to_db( fix_access, 'N6', Point2D( 70, 0 ), srid, ntw_id, ntw_graph_id )

    # Add pipes.
    th_net.write_round_pipe_to_db( fix_access, 'SRCE-N0', nodes_data['SRCE'], nodes_data['N0'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N0-SNK1', nodes_data['N0'], nodes_data['SNK1'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N1-SNK2', nodes_data['N1'], nodes_data['SNK2'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N2-SNK3', nodes_data['N2'], nodes_data['SNK3'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N2-SNK4', nodes_data['N2'], nodes_data['SNK4'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N2-SNK5', nodes_data['N2'], nodes_data['SNK5'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N3-SNK6', nodes_data['N3'], nodes_data['SNK6'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N4-SNK7', nodes_data['N4'], nodes_data['SNK7'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N5-SNK8', nodes_data['N5'], nodes_data['SNK8'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N6-SNK9', nodes_data['N6'], nodes_data['SNK9'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N0-N1', nodes_data['N0'], nodes_data['N1'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N1-N2', nodes_data['N1'], nodes_data['N2'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N2-N3', nodes_data['N2'], nodes_data['N3'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N3-N4', nodes_data['N3'], nodes_data['N4'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N4-N5', nodes_data['N4'], nodes_data['N5'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )
    th_net.write_round_pipe_to_db( fix_access, 'N5-N6', nodes_data['N5'], nodes_data['N6'], srid, ntw_id, ntw_graph_id, 'distribution-pipe' )

    fix_access.commit_citydb_session()


def test_sim_utn_thermal_pandathermal( fix_connect, fix_thermal_network_id ):

    # Instantiate reader.
    pth_reader = PandaThermalModelDBReader( fix_connect )

    # Create simulation model from database.
    net = pth_reader.get_net( network_id = fix_thermal_network_id )

    # Check number of elements in the simulation model.
    assert( len( net.nodes ) == 17 )
    assert( len( net.edges ) == 16 )

    # Calculate the maximal mass flows.
    pipes_max_m_dot = pth.compute_pipes_max_m_dot( net, dt=40 )

    print(pipes_max_m_dot)
    # Check results.
    assert( pipes_max_m_dot[('SRCE', 'N0')] == pytest.approx( 0.81, 1e-4 ) )
    assert( pipes_max_m_dot[('N0','SNK1')] == pytest.approx( 0.05, 1e-4 ) )
    assert( pipes_max_m_dot[('N0','N1')] == pytest.approx( 0.76, 1e-4 ) )
    assert( pipes_max_m_dot[('N1','SNK2')] == pytest.approx( 0.10, 1e-4 ) )
    assert( pipes_max_m_dot[('N1','N2')] == pytest.approx( 0.67, 1e-4 ) )
    assert( pipes_max_m_dot[('N2','SNK3')] == pytest.approx( 0.05, 1e-4 ) )
    assert( pipes_max_m_dot[('N2','SNK4')] == pytest.approx( 0.24, 1e-4 ) )
    assert( pipes_max_m_dot[('N2','SNK5')] == pytest.approx( 0.05, 1e-4 ) )
    assert( pipes_max_m_dot[('N2','N3')] == pytest.approx( 0.33, 1e-4 ) )
    assert( pipes_max_m_dot[('N3','SNK6')] == pytest.approx( 0.10, 1e-4 ) )
    assert( pipes_max_m_dot[('N3','N4')] == pytest.approx( 0.24, 1e-4 ) )
    assert( pipes_max_m_dot[('N4','SNK7')] == pytest.approx( 0.05, 1e-4 ) )
    assert( pipes_max_m_dot[('N4','N5')] == pytest.approx( 0.19, 1e-4 ) )
    assert( pipes_max_m_dot[('N5','N6')] == pytest.approx( 0.05, 1e-4 ) )
    assert( pipes_max_m_dot[('N5','SNK8')] == pytest.approx( 0.14, 1e-4 ) )
    assert( pipes_max_m_dot[('N6','SNK9')] == pytest.approx( 0.05, 1e-4 ) )


def test_fill_citydb_utn_gas( fix_access, fix_gas_network_id, fix_srid ):

    # Define spatial reference ID.
    srid = fix_srid

    # Create network and network graph.
    ( ntw_id, ntw_graph_id ) = gas_net.write_network_to_db(
        fix_access,
        name = 'test_gas_network',
        id = fix_gas_network_id
        )

    # Add gas network nodes.
    node_f = gas_net.write_network_node_to_db( fix_access, 'node-NF', 'MP', Point2D( 0., 0. ), srid, ntw_id, ntw_graph_id )
    node_0 = gas_net.write_network_node_to_db( fix_access, 'node-N0', 'MP', Point2D( 100., 0. ), srid, ntw_id, ntw_graph_id )
    node_1 = gas_net.write_network_node_to_db( fix_access, 'node-N1', 'BP', Point2D( 105., 0. ), srid, ntw_id, ntw_graph_id )
    node_2 = gas_net.write_network_node_to_db( fix_access, 'node-N2', 'BP', Point2D( 265., 366.606 ), srid, ntw_id, ntw_graph_id )
    node_3 = gas_net.write_network_node_to_db( fix_access, 'node-N3', 'BP', Point2D( 605., 0. ), srid, ntw_id, ntw_graph_id )

    # Add gas pipes.
    gas_net.write_round_pipe_to_db( fix_access, 'pipe-NF-N0', node_f, node_0, srid, ntw_id, ntw_graph_id,int_diameter = 0.05, int_diameter_unit = 'm' )
    gas_net.write_round_pipe_to_db( fix_access, 'pipe-N1-N2', node_1, node_2, srid, ntw_id, ntw_graph_id,int_diameter = 0.05, int_diameter_unit = 'm' )
    gas_net.write_round_pipe_to_db( fix_access, 'pipe-N1-N3', node_1, node_3, srid, ntw_id, ntw_graph_id,int_diameter = 0.05, int_diameter_unit = 'm' )
    gas_net.write_round_pipe_to_db( fix_access, 'pipe-N2-N3', node_2, node_3, srid, ntw_id, ntw_graph_id,int_diameter = 0.05, int_diameter_unit = 'm' )

    # Add sinks.
    gas_net.write_gas_sink_to_db( fix_access, 'sink-N2', node_2, 10., 'kW', srid, ntw_id, ntw_graph_id )
    gas_net.write_gas_sink_to_db( fix_access, 'sink-N3', node_3, 15., 'kW', srid, ntw_id, ntw_graph_id )

    # Add gas network station.
    gas_net.write_station_to_db( fix_access, 'station-N0-N1', node_0, node_1, 50., 0.025E5, srid, ntw_id, ntw_graph_id )

    # Add external gas feeder.
    gas_net.write_feeder_to_db( fix_access, 'feeder-F', node_f, 50., 0.9E5, srid, ntw_id, ntw_graph_id )

    fix_access.commit_citydb_session()


def test_sim_utn_gas_pandangas( fix_connect, fix_gas_network_id ):

    # Instantiate reader.
    pg_reader = PandaNGasModelDBReader( fix_connect )

    # Create simulation model from database.
    net = pg_reader.get_net( network_id = fix_gas_network_id )

    # Check number of elements in the simulation model.
    assert( len( net.station ) == 1 )
    assert( len( net.pipe ) == 4 )
    assert( len( net.feeder ) == 1 )
    assert( len( net.load ) == 2 )
    assert( len( net.bus ) == 5 )

    scaled_loads = gas_sim._scaled_loads_as_dict( net )
    assert( scaled_loads['node-N2'] == 0.000262 )
    assert( scaled_loads['node-N3'] == 0.000394 )

    p_min_loads = gas_sim._p_min_loads_as_dict( net )
    assert( p_min_loads['node-N2'] == 2200.0 )
    assert( p_min_loads['node-N3'] == 2200.0 )

    p_nom_feed = gas_sim._p_nom_feed_as_dict( net )
    assert( p_nom_feed['node-NF'] == 90000.0 )
    assert( p_nom_feed['node-N1'] == 2500.0 )

    #with pytest.warns( PendingDeprecationWarning ) as record:
    p_nodes, m_dot_pipes, m_dot_nodes, gas = gas_sim._run_sim( net )

    #assert( len( record ) == 1 )

    assert( p_nodes['node-N1'] == 2500.0 )
    assert( p_nodes['node-N2'] == 1962.7 )
    assert( p_nodes['node-N3'] == 1827.8 )
    assert( m_dot_pipes['pipe-N1-N2'] == 0.000328 )
    assert( m_dot_pipes['pipe-N1-N3'] == 0.000328 )
    assert( m_dot_pipes['pipe-N2-N3'] == 6.6e-05 )
    assert( m_dot_nodes['node-N1'] == -0.000656 )
    assert( m_dot_nodes['node-N2'] == 0.000262 )
    assert( m_dot_nodes['node-N3'] == 0.000394 )
    #assert( pipes_max_m_dot[('N6','SNK9')] == pytest.approx( 0.05, 1e-4 ) )
