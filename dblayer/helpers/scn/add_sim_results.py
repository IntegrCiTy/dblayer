from dblayer import *
from dblayer.func.func_citydb_view_scn import *

from collections import namedtuple


# Tuple containing a single simulation result.
SimResultValue = namedtuple(
    'SimResultValue',
    [ 'name', 'object_id', 'value', 'unit' ]
    )


# Tuple containing a time series of simulation results.
SimResultRegularTimeSeries = namedtuple(
    'SimResultRegularTimeSeries',
    [ 'name', 'object_id',
      'values_array', 'values_unit',
      'time_interval', 'time_interval_unit',
      'temporal_extent_begin', 'temporal_extent_end',
      'acquisition_method', 'interpolation_type' ]
    )


def add_sim_results_values(
    access,
    sim_name,
    sim_results
    ):
    '''
    Associate simulation results to city objects.
    For each city object, the associated results has to be a scalar value (int, float, bool, str).

    :param access: instance of database interface (DBAccess)
    :param sim_name: name of the simulation (str)
    :param sim_results: list of simulation results (list of SimResultValue)
    :return: ID of the scenario
    '''
    if not isinstance( access, DBAccess ):
        raise TypeError( 'parameter \'access\' must be of type \'DBAccess\'' )

    scenario_id = access.add_citydb_object(
        insert_scenario,
        name = sim_name
        )

    for res in sim_results:
        if not isinstance( res, SimResultValue ):
            raise RuntimeError( 'simulation results must be of type \'SimResultValue\'' )
        
        if isinstance( res.value, int ):
            access.add_citydb_object(
                insert_scenario_parameter,
                name = res.name,
                sim_name = sim_name,
                intval = res.value,
                unit = res.unit,
                cityobject_id = res.object_id,
                scenario_id = scenario_id )
        elif isinstance( res.value, float ):
            access.add_citydb_object(
                insert_scenario_parameter,
                name = res.name,
                sim_name = sim_name,
                realval = res.value,
                unit = res.unit,
                cityobject_id = res.object_id,
                scenario_id = scenario_id )
        elif isinstance( res.value, bool ):
            access.add_citydb_object(
                insert_scenario_parameter,
                name = res.name,
                sim_name = sim_name,
                booleanval = res.value,
                unit = res.unit,
                cityobject_id = res.object_id,
                scenario_id = scenario_id )
        elif isinstance( res.value, str ):
            access.add_citydb_object(
                insert_scenario_parameter,
                name = res.name,
                sim_name = sim_name,
                strval = res.value,
                unit = res.unit,
                cityobject_id = res.object_id,
                scenario_id = scenario_id )
        else:
            raise RuntimeError( 'Type of result not supported: {}'.format( type( res.value ) ) )

    return scenario_id



def add_sim_results_regular_time_series(
    access,
    sim_name,
    sim_results
    ):
    '''
    Associate simulation results to city objects.
    For each city object, the associated results has to be a regular time series.

    :param access: instance of database interface (DBAccess)
    :param sim_name: name of the simulation (str)
    :param sim_results: list of simulation results (list of SimResultRegularTimeSeries)
    :return: ID of the scenario
    '''
    if not isinstance( access, DBAccess ):
        raise TypeError( 'parameter \'access\' must be of type \'DBAccess\'' )

    scenario_id = access.add_citydb_object(
        insert_scenario,
        name = sim_name
        )

    for res in sim_results:
        if not isinstance( res, SimResultRegularTimeSeries ):
            raise RuntimeError( 'simulation results must be of type \'SimResultRegularTimeSeries\'' )

        ts_id = access.add_citydb_object(
            insert_regular_time_series,
            name = 'ts_{}'.format( res.name ),
            acquisition_method = res.acquisition_method,
            interpolation_type = res.interpolation_type,
            values_array = res.values_array,
            values_unit = res.values_unit,
            temporal_extent_begin = res.temporal_extent_begin,
            temporal_extent_end = res.temporal_extent_end,
            time_interval = res.time_interval,
            time_interval_unit = res.time_interval_unit
            )

        access.add_citydb_object(
            insert_scenario_parameter,
            name = res.name,
            sim_name = sim_name,
            time_series_id = ts_id,
            cityobject_id = res.object_id,
            scenario_id = scenario_id
            )
        
    return scenario_id
