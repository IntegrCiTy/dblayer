import pytest

import os
import sqlalchemy.orm.exc

from dblayer import *
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
def fix_create():
    '''
    Fixture for testing. Creates a simpple ready-to-run co-simulation setup.

    :return: simulation setup with meta, models, nodes, links, groups, sequence and steps implemented (ictdeploy.Simulator)
    '''
    # Create simulation setup.
    sim = ictdeploy.Simulator()

    # Add meta model.
    sim.edit.add_meta(
        name='BaseMeta',
        set_attrs=['a'],
        get_attrs=['b']
    )

    # Add model based on meta model.
    sim.edit.add_model(
        name='BaseModel',
        meta='BaseMeta',
        image='integrcity/ict-simple',
        wrapper=os.path.join('tests', 'wrappers', 'base_wrap.py'),
        command=None,
        files=[os.path.join('tests', 'files_to_add', 'empty_file_for_testing_purpose.txt')]
    )

    # Add node based on model.
    sim.edit.add_node(
        name='Base0',
        model='BaseModel',
        init_values={'c': 0.5},
        is_first=True
    )

    # Add another node based on model.
    sim.edit.add_node(
        name='Base1',
        model='BaseModel',
        init_values={'c': 0.25}
    )

    # Define links between nodes.
    sim.edit.add_link(get_node='Base0', get_attr='b', set_node='Base1', set_attr='a')
    sim.edit.add_link(get_node='Base1', get_attr='b', set_node='Base0', set_attr='a')

    # Define simulation groups and sequence.
    grp0 = sim.create_group('Base0')
    grp1 = sim.create_group('Base1')
    sim.create_sequence(grp0, grp1)

    # Define simulation time steps.
    sim.create_steps([60] * 10)

    return sim


def test_cleanup_schema( fix_connect ):
    access = DBAccess()
    access.cleanup_schema( fix_connect )


def test_read_db( fix_connect ):
    with pytest.raises( sqlalchemy.orm.exc.NoResultFound ) as e:
        reader = DBReader()
        # Try to read a scenario that does not exist.
        sim = reader.read_from_db( 'TestSimX', fix_connect )
    assert 'No row was found for one()' in str( e )


def test_write_db( fix_connect, fix_create ):
    writer = DBWriter( fix_create )
    writer.write_to_db( 'TestSim', fix_connect )
    
#         # NOT YET IMPLEMENTED: Try to write a scenario with an already existing name to database.
#         try:
#             writer.write_to_db( 'TestSim', self.connect )
#         except RuntimeError as e:
#             expected_message = ''
#             self.assertEqual( str( e ) )


def test_write_and_read_db( fix_connect, fix_create ):
    # Define simulation setup name.
    sim_name = 'TestSim2'

    # Write simulation setup to database. Do not write meta models and models, because
    # they have already been written to the database in one of the previous tests.
    sim_write = fix_create
    writer = DBWriter( sim_write )
    writer.write_to_db( sim_name, fix_connect, write_meta_models = False, write_models = False )

    # Read simulation setup from database.
    reader = DBReader()
    sim_read = reader.read_from_db( sim_name, fix_connect )

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
    g_dict =  sim_read.edit.interaction_graph
    assert len( g_dict[ 'links' ] ) == 2
    assert len( g_dict[ 'nodes' ] ) == 2
    assert  sim_read.steps == [ 60, 60, 60, 60, 60, 60, 60, 60, 60, 60 ]
    assert  sim_read.sequence == [ ( 'Base0', ), ( 'Base1', ) ]