from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import array


def insert_scenario(
    id = None,
    scenario_parent_id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    class_name = None,
    instant = None,
    period_begin = None,
    period_end = None,
    citymodel_id = None,
    cityobject_id = None,
    envelope = None,
    creator_name = None,
    creation_date = None
    ):
    '''
    Define function call to insert scenario.
    '''
    return func.citydb_view.scn2_insert_scenario(
        id, # integer, default: NULL::integer
        scenario_parent_id, # integer, default: NULL::integer
        gmlid, # varchar, default: NULL::character varying
        gmlid_codespace, # varchar, default: NULL::character varying
        name, # varchar, default: NULL::character varying
        name_codespace, # varchar, default: NULL::character varying
        description, # text, default: NULL::text
        class_name, # varchar, default: NULL::character varying
        instant, # timestamptz(0), default: NULL::timestamptz
        period_begin, # date, default: NULL::date
        period_end, # date, default: NULL::date
        citymodel_id, # integer, default: NULL::integer
        cityobject_id, # integer, default: NULL::integer
        envelope, # geometry(PolygonZ), default: NULL::geometry
        creator_name, # varchar, default: NULL::character varying
        creation_date, # timestamptz(0), default: NULL::timestamptz
        )


def insert_scenario_parameter(
    id = None,
    type = None,
    name = None,
    name_codespace = None,
    description = None,
    class_name = None,
    constraint_type = None,
    sim_name = None,
    sim_description = None,
    sim_reference = None,
    aggregation_type = None,
    temp_aggregation = None,
    strval = None,
    booleanval = None,
    intval = None,
    realval = None,
    unit = None,
    dateval = None,
    urival = None,
    geomval = None,
    time_series_id = None,
    cityobject_id = None,
    scenario_id = None
    ):
    '''
    Define function call to insert scenario parameter.
    '''
    return func.citydb_view.scn2_insert_scenario_parameter(
        id, # integer, default: NULL::integer
        type, # varchar, default: NULL::character varying
        name, # varchar, default: NULL::character varying
        name_codespace, # varchar, default: NULL::character varying
        description, # text, default: NULL::text
        class_name, # varchar, default: NULL::character varying
        constraint_type, # varchar, default: NULL::character varying
        sim_name, # varchar, default: NULL::character varying
        sim_description, # varchar, default: NULL::character varying
        sim_reference, # varchar, default: NULL::character varying
        aggregation_type, # varchar, default: NULL::character varying
        temp_aggregation, # varchar, default: NULL::character varying
        strval, # varchar, default: NULL::character varying
        booleanval, # numeric(1,0), default: NULL::numeric
        intval, # integer, default: NULL::integer
        realval, # numeric, default: NULL::numeric
        unit, # varchar, default: NULL::character varying
        dateval, # date, default: NULL::character date
        urival, # varchar, default: NULL::character varying
        geomval, # geometry(GeometryZ), default: NULL::geometry
        time_series_id, # integer, default: NULL::integer
        cityobject_id, # integer, default: NULL::integer
        scenario_id # integer, default: NULL::integer
        )


def insert_regular_time_series(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    acquisition_method = 'Unknown',
    interpolation_type = 'Continuous',
    quality_description = None,
    source = None,
    values_array = None,
    values_unit = None,
    temporal_extent_begin = None,
    temporal_extent_end = None,
    time_interval = None,
    time_interval_unit = None
    ):
    '''
    Define function call to insert regular time series.
    '''
    if values_array is None: values_array = []

    if acquisition_method not in [ 'Measurement', 'Simulation', 'CalibratedSimulation', 'Estimation', 'Unknown' ]:
        raise RuntimeError( 'invalid acquisition method' )

    if interpolation_type not in [ 'AverageInPrecedingInterval', 'AverageInSucceedingInterval','ConstantInPrecedingInterval', 'ConstantInSucceedingInterval', 'Continuous', 'Discontinuous','InstantaneousTotal', 'MaximumInPrecedingInterval', 'MaximumInSucceedingInterval','MinimumInPrecedingInterval', 'MinimumInSucceedingInterval', 'PrecedingTotal', 'SucceedingTotal' ]:
        raise RuntimeError( 'invalid interpolation type' )

    return func.citydb_view.scn2_insert_regular_time_series(
        id, # integer, default: NULL::integer
        gmlid, # default: NULL::character varying
        gmlid_codespace, # varchar, default: NULL::character varying
        name, # varchar, default: NULL::character varying
        name_codespace, # varchar, default: NULL::character varying
        description, # text, default: NULL::text
        acquisition_method, # varchar, default: NULL::character varying
        interpolation_type, # varchar, default: NULL::character varying
        quality_description, # text, default: NULL::character varying
        source, # varchar, default: NULL::character varying
        values_array, # numeric[], default: NULL::numeric[]
        values_unit, # varchar, default: NULL::character varying
        len( values_array ), # integer, default: NULL::integer
        temporal_extent_begin, # timestamp with time zone, default: NULL::timestamp with time zone
        temporal_extent_end, # timestamp with time zone, default: NULL::timestamp with time zone
        time_interval, # numeric, default: NULL::numeric
        time_interval_unit, # varchar, default: NULL::character varying
        )
