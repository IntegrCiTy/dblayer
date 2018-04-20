import pytest

import os
import sqlalchemy.orm.exc

from dblayer import *
from dblayer.citydb_view_func import *
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


def test_cleanup_citydb_schema( fix_access ):
    fix_access.cleanup_citydb_schema()


def test_cleanup_simpkg_schema( fix_access ):
    fix_access.cleanup_simpkg_schema()


def test_map_invalid_class( fix_access ):
    with pytest.raises( RuntimeError ) as e:
        fix_access.map_citydb_object_class( 'InvalidObjectClassName' )
    assert 'unknown object class: InvalidObjectClassName' in str( e )


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
    buildings = fix_access.get_citydb_objects( "Building" )

    # Expect a query result with two entries.
    assert len( buildings ) == 2

    # Retrieve building data from user-friendly 3DCityDB view (citydb_view.building).
    with pytest.warns( RuntimeWarning ) as record:
        # Retrieve the class mapped to the view.
        Buildings = fix_access.map_citydb_object_class( "Building", schema = 'citydb_view' )

        # Use the mapped class to define filter conditions.
        conditions = [ Buildings.name == 'BUILDING_02' ]

        # Retrieve the data.
        buildings = fix_access.get_citydb_objects( "Building", conditions = conditions )

        # Expect a query result with only one entry.
        assert len( buildings ) == 1

    # Check that only one warning was raised.
    assert len( record ) == 1

    # Check that the message matches.
    assert record[0].message.args[0] == 'Class Building will has already been mapped from table: building (schema: citydb). It will be re-mapped from table: building (schema: citydb_view).'


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
    sim_name = 'TestSim2'

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