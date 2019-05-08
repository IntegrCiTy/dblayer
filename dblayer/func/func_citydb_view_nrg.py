from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import array


def insert_boiler(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    envelope = None,
    creation_date = None,
    termination_date = None,
    relative_to_terrain = None,
    relative_to_water = None,
    last_modification_date = None,
    updating_person = None,
    reason_for_update = None,
    lineage = None,
    model = None,
    nbr = None,
    year_of_manufacture = None,
    inst_nom_pwr = None,
    inst_nom_pwr_unit = None,
    nom_effcy = None,
    effcy_indicator = None,
    start_of_life = None,
    life_expect_value = None,
    life_expect_value_unit = None,
    main_maint_interval = None,
    main_maint_interval_unit = None,
    inst_in_ctyobj_id = None,
    cityobject_id = None,
    condensation = None
    ):
    """
    Define function call to insert boiler into the database.
    """
    return func.citydb_view.nrg8_insert_boiler(
        id, # integer, default:: NULL::integer
        gmlid, # character varying, default:: NULL::character varying
        gmlid_codespace, # character varying, default:: NULL::character varying
        name, # character varying, default:: NULL::character varying
        name_codespace, # character varying, default:: NULL::character varying
        description, # character varying, default:: NULL::character varying
        envelope, # geometry, default:: NULL::geometry
        creation_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        termination_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        relative_to_terrain, # character varying, default:: NULL::character varying
        relative_to_water, # character varying, default:: NULL::character varying
        last_modification_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        updating_person, # character varying, default:: NULL::character varying
        reason_for_update, # character varying, default:: NULL::character varying
        lineage, # character varying, default:: NULL::character varying
        model, # character varying, default:: NULL::character varying
        nbr, # integer, default:: NULL::integer
        year_of_manufacture, # integer, default:: NULL::integer
        inst_nom_pwr, # numeric, default:: NULL::numeric
        inst_nom_pwr_unit, # character varying, default:: NULL::character varying
        nom_effcy, # numeric, default:: NULL::numeric
        effcy_indicator, # character varying, default:: NULL::character varying
        start_of_life, # date, default:: NULL::date
        life_expect_value, # numeric, default:: NULL::numeric
        life_expect_value_unit, # character varying, default:: NULL::character varying
        main_maint_interval, # numeric, default:: NULL::numeric
        main_maint_interval_unit, # character varying, default:: NULL::character varying
        inst_in_ctyobj_id, # integer, default:: NULL::integer
        cityobject_id, # integer, default:: NULL::integer
        condensation # numeric, default:: NULL::numeric
        )


def insert_building(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    envelope = None,
    creation_date = None,
    termination_date = None,
    relative_to_terrain = None,
    relative_to_water = None,
    last_modification_date = None,
    updating_person = None,
    reason_for_update = None,
    lineage = None,
    building_parent_id = None,
    building_root_id = None,
    class_name = None,
    class_codespace = None,
    function = None,
    function_codespace = None,
    usage = None,
    usage_codespace = None,
    year_of_construction = None,
    year_of_demolition = None,
    roof_type = None,
    roof_type_codespace = None,
    measured_height = None,
    measured_height_unit = None,
    storeys_above_ground = None,
    storeys_below_ground = None,
    storey_heights_above_ground = None,
    storey_heights_ag_unit = None,
    storey_heights_below_ground = None,
    storey_heights_bg_unit = None,
    lod1_terrain_intersection = None,
    lod2_terrain_intersection = None,
    lod3_terrain_intersection = None,
    lod4_terrain_intersection = None,
    lod2_multi_curve = None,
    lod3_multi_curve = None,
    lod4_multi_curve = None,
    lod0_footprint_id = None,
    lod0_roofprint_id = None,
    lod1_multi_surface_id = None,
    lod2_multi_surface_id = None,
    lod3_multi_surface_id = None,
    lod4_multi_surface_id = None,
    lod1_solid_id = None,
    lod2_solid_id = None,
    lod3_solid_id = None,
    lod4_solid_id = None ):
    """
    Define function call to insert building into the database.
    """
    return func.citydb_view.nrg8_insert_building(
        id, # integer, default:: NULL::integer,
        gmlid, # character varying, default:: NULL::character varying
        gmlid_codespace, # character varying, default:: NULL::character varying
        name, # character varying, default:: NULL::character varying
        name_codespace, # character varying, default:: NULL::character varying
        description, # character varying, default:: NULL::character varying
        envelope, # geometry, default:: NULL::geometry
        creation_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        termination_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        relative_to_terrain, # character varying, default:: NULL::character varying
        relative_to_water, # character varying, default:: NULL::character varying
        last_modification_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        updating_person, # character varying, default:: NULL::character varying
        reason_for_update, # character varying, default:: NULL::character varying
        lineage, # character varying, default:: NULL::character varying
        building_parent_id, # integer, default:: NULL::integer
        building_root_id, # integer, default:: NULL::integer
        class_name, # character varying, default:: NULL::character varying
        class_codespace, # character varying, default:: NULL::character varying
        function, # character varying, default:: NULL::character varying
        function_codespace, # character varying, default:: NULL::character varying
        usage, # character varying, default:: NULL::character varying
        usage_codespace, # character varying, default:: NULL::character varying
        year_of_construction, # date, default:: NULL::date
        year_of_demolition, # date, default:: NULL::date
        roof_type, # character varying, default:: NULL::character varying
        roof_type_codespace, # character varying, default:: NULL::character varying
        measured_height, # double precision, default:: NULL::double precision
        measured_height_unit, # character varying, default:: NULL::character varying
        storeys_above_ground, # numeric, default:: NULL::numeric
        storeys_below_ground, # numeric, default:: NULL::numeric
        storey_heights_above_ground, # character varying, default:: NULL::character varying
        storey_heights_ag_unit, # character varying, default:: NULL::character varying
        storey_heights_below_ground, # character varying, default:: NULL::character varying
        storey_heights_bg_unit, # character varying, default:: NULL::character varying
        lod1_terrain_intersection, # geometry, default:: NULL::geometry
        lod2_terrain_intersection, # geometry, default:: NULL::geometry
        lod3_terrain_intersection, # geometry, default:: NULL::geometry
        lod4_terrain_intersection, # geometry, default:: NULL::geometry
        lod2_multi_curve, # geometry, default:: NULL::geometry
        lod3_multi_curve, # geometry, default:: NULL::geometry
        lod4_multi_curve, # geometry, default:: NULL::geometry
        lod0_footprint_id, # integer, default:: NULL::integer
        lod0_roofprint_id, # integer, default:: NULL::integer
        lod1_multi_surface_id, # integer, default:: NULL::integer
        lod2_multi_surface_id, # integer, default:: NULL::integer
        lod3_multi_surface_id, # integer, default:: NULL::integer
        lod4_multi_surface_id, # integer, default:: NULL::integer
        lod1_solid_id, # integer, default:: NULL::integer
        lod2_solid_id, # integer, default:: NULL::integer
        lod3_solid_id, # integer, default:: NULL::integer
        lod4_solid_id # integer, default:: NULL::integer
        )


def insert_energy_demand(
        id = None,
        gmlid = None,
        gmlid_codespace = None,
        name = None,
        name_codespace = None,
        description = None,
        end_use = None,
        max_load = None,
        max_load_unit = None,
        time_series_id = None,
        cityobject_id = None
    ):
    """
    Define function call to insert energy demand into the database.
    """
    return func.citydb_view.nrg8_insert_energy_demand(
        id, # integer, default:: NULL::integer
        gmlid, # character varying, default:: NULL::character varying
        gmlid_codespace, # character varying, default:: NULL::character varying
        name, # character varying, default:: NULL::character varying
        name_codespace, # character varying, default:: NULL::character varying
        description, # text, default:: NULL::text
        end_use, # character varying, default:: NULL::character varying
        max_load, # numeric, default:: NULL::numeric
        max_load_unit, # character varying, default:: NULL::character varying
        time_series_id, # integer, default:: NULL::integer
        cityobject_id # integer, default:: NULL::integer
        )


def insert_heat_pump(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    envelope = None,
    creation_date = None,
    termination_date = None,
    relative_to_terrain = None,
    relative_to_water = None,
    last_modification_date = None,
    updating_person = None,
    reason_for_update = None,
    lineage = None,
    model = None,
    nbr = None,
    year_of_manufacture = None,
    inst_nom_pwr = None,
    inst_nom_pwr_unit = None,
    nom_effcy = None,
    effcy_indicator = None,
    start_of_life = None,
    life_expect_value = None,
    life_expect_value_unit = None,
    main_maint_interval = None,
    main_maint_interval_unit = None,
    inst_in_ctyobj_id = None,
    cityobject_id = None,
    heat_source = None,
    cop_source_temp = None,
    cop_source_temp_unit = None,
    cop_oper_temp = None,
    cop_oper_temp_unit = None
    ):
    """
    Define function call to insert heat pump into the database.
    """
    return func.citydb_view.nrg8_insert_heat_pump(
        id, # integer,, default::: NULL::integer
        gmlid, # character varying,, default::: NULL::character varying
        gmlid_codespace, # character varying,, default::: NULL::character varying
        name, # character varying,, default::: NULL::character varying
        name_codespace, # character varying,, default::: NULL::character varying
        description, # character varying,, default::: NULL::character varying
        envelope, # geometry,, default::: NULL::geometry
        creation_date, # timestamp with time zone,, default::: NULL::timestamp with time zone
        termination_date, # timestamp with time zone,, default::: NULL::timestamp with time zone
        relative_to_terrain, # character varying,, default::: NULL::character varying
        relative_to_water, # character varying,, default::: NULL::character varying
        last_modification_date, # timestamp with time zone,, default::: NULL::timestamp with time zone
        updating_person, # character varying,, default::: NULL::character varying
        reason_for_update, # character varying,, default::: NULL::character varying
        lineage, # character varying,, default::: NULL::character varying
        model, # character varying,, default::: NULL::character varying
        nbr, # integer,, default::: NULL::integer
        year_of_manufacture, # integer,, default::: NULL::integer
        inst_nom_pwr, # numeric,, default::: NULL::numeric
        inst_nom_pwr_unit, # character varying,, default::: NULL::character varying
        nom_effcy, # numeric,, default::: NULL::numeric
        effcy_indicator, # character varying,, default::: NULL::character varying
        start_of_life, # date,, default::: NULL::date
        life_expect_value, # numeric,, default::: NULL::numeric
        life_expect_value_unit, # character varying,, default::: NULL::character varying
        main_maint_interval, # numeric,, default::: NULL::numeric
        main_maint_interval_unit, # character varying,, default::: NULL::character varying
        inst_in_ctyobj_id, # integer,, default::: NULL::integer
        cityobject_id, # integer,, default::: NULL::integer
        heat_source, # character varying,, default::: NULL::character varying
        cop_source_temp, # numeric,, default::: NULL::numeric
        cop_source_temp_unit, # character varying,, default::: NULL::character varying
        cop_oper_temp, # numeric,, default::: NULL::numeric
        cop_oper_temp_unit, # character varying,, default::: NULL::character varying
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
    """
    Define function call to insert regular time series into the database.
    """
    if values_array is None: values_array = []

    if acquisition_method not in [ 'Measurement', 'Simulation', 'CalibratedSimulation', 'Estimation', 'Unknown' ]:
        raise RuntimeError( 'invalid acquisition method' )

    if interpolation_type not in [ 'AverageInPrecedingInterval', 'AverageInSucceedingInterval','ConstantInPrecedingInterval', 'ConstantInSucceedingInterval', 'Continuous', 'Discontinuous','InstantaneousTotal', 'MaximumInPrecedingInterval', 'MaximumInSucceedingInterval','MinimumInPrecedingInterval', 'MinimumInSucceedingInterval', 'PrecedingTotal', 'SucceedingTotal' ]:
        raise RuntimeError( 'invalid interpolation type' )

    return func.citydb_view.nrg8_insert_regular_time_series(
        id, # integer, default:: NULL::integer
        gmlid, # character varying, default:: NULL::character varying
        gmlid_codespace, # character varying, default:: NULL::character varying
        name, # character varying, default:: NULL::character varying
        name_codespace, # character varying, default:: NULL::character varying
        description, # text, default:: NULL::text
        acquisition_method, # character varying, default:: NULL::character varying
        interpolation_type, # character varying, default:: NULL::character varying
        quality_description, # text, default:: NULL::text
        source, # character varying, default:: NULL::character varying
        values_array, # numeric[], default:: NULL::numeric[]
        values_unit, # character varying, default:: NULL::character varying
        len( values_array ), # integer, default:: NULL::integer
        temporal_extent_begin, # timestamp with time zone, default:: NULL::timestamp with time zone
        temporal_extent_end, # timestamp with time zone, default:: NULL::timestamp with time zone
        time_interval, # numeric, default:: NULL::numeric
        time_interval_unit # character varying, default:: NULL::character varying
        )


def insert_electrical_appliances(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    envelope = None,
    creation_date = None,
    termination_date = None,
    relative_to_terrain = None,
    relative_to_water = None,
    last_modification_date = None,
    updating_person = None,
    reason_for_update = None,
    lineage = None,
    heat_diss_tot_value = None,
    heat_diss_tot_value_unit = None,
    heat_diss_conv = None,
    heat_diss_lat = None,
    heat_diss_rad = None,
    electr_pwr = None,
    electr_pwr_unit = None,
    oper_sched_id = None,
    usage_zone_id = None,
    building_unit_id = None
    ):
    '''
    Define function call to insert electrical appliance into the database.
    '''
    return func.citydb_view.nrg8_insert_electrical_appliances(
        id, # integer, default:: NULL::integer
        gmlid, # character varying, default:: NULL::character varying
        gmlid_codespace, # character varying, default:: NULL::character varying
        name, # character varying, default:: NULL::character varying
        name_codespace, # character varying, default:: NULL::character varying
        description, # character varying, default:: NULL::character varying
        envelope, # geometry, default:: NULL::geometry
        creation_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        termination_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        relative_to_terrain, # character varying, default:: NULL::character varying
        relative_to_water, # character varying, default:: NULL::character varying
        last_modification_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        updating_person, # character varying, default:: NULL::character varying
        reason_for_update, # character varying, default:: NULL::character varying
        lineage, # character varying, default:: NULL::character varying
        heat_diss_tot_value, # numeric, default:: NULL::numeric
        heat_diss_tot_value_unit, # character varying, default:: NULL::character varying
        heat_diss_conv, # numeric, default:: NULL::numeric
        heat_diss_lat, # numeric, default:: NULL::numeric
        heat_diss_rad, # numeric, default:: NULL::numeric
        electr_pwr, # numeric, default:: NULL::numeric
        electr_pwr_unit, # character varying, default:: NULL::character varying
        oper_sched_id, # integer, default:: NULL::integer
        usage_zone_id, # integer, default:: NULL::integer
        building_unit_id # integer, NULL::integer
        )


def insert_dhw_facilities(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    envelope = None,
    creation_date = None,
    termination_date = None,
    relative_to_terrain = None,
    relative_to_water = None,
    last_modification_date = None,
    updating_person = None,
    reason_for_update = None,
    lineage = None,
    heat_diss_tot_value = None,
    heat_diss_tot_value_unit = None,
    heat_diss_conv = None,
    heat_diss_lat = None,
    heat_diss_rad = None,
    nbr_of_baths = None,
    nbr_of_showers = None,
    nbr_of_washbasins = None,
    water_strg_vol = None,
    water_strg_vol_unit = None,
    oper_sched_id = None,
    usage_zone_id = None,
    building_unit_id = None
    ):
    '''
    Define function call to onsert DHW facility.
    '''
    return func.citydb_view.nrg8_insert_dhw_facilities(
        id, # integer, default: NULL::integer
        gmlid, # character varying, default: NULL::character varying
        gmlid_codespace, # character varying, default: NULL::character varying
        name, # character varying, default: NULL::character varying
        name_codespace, # character varying, default: NULL::character varying
        description, # character varying, default: NULL::character varying
        envelope, # geometry, default: NULL::geometry
        creation_date, # timestamp with time zone, default: NULL::timestamp with time zone
        termination_date, # timestamp with time zone, default: NULL::timestamp with time zone
        relative_to_terrain, # character varying, default: NULL::character varying
        relative_to_water, # character varying, default: NULL::character varying
        last_modification_date, # timestamp with time zone, default: NULL::timestamp with time zone
        updating_person, # character varying, default: NULL::character varying
        reason_for_update, # character varying, default: NULL::character varying
        lineage, # character varying, default: NULL::character varying
        heat_diss_tot_value, # numeric, default: NULL::numeric
        heat_diss_tot_value_unit, # character varying, default: NULL::character varying
        heat_diss_conv, # numeric, default: NULL::numeric
        heat_diss_lat, # numeric, default: NULL::numeric
        heat_diss_rad, # numeric, default: NULL::numeric
        nbr_of_baths, # integer, default: NULL::integer
        nbr_of_showers, # integer, default: NULL::integer
        nbr_of_washbasins, # integer, default: NULL::integer
        water_strg_vol, # numeric, default: NULL::numeric
        water_strg_vol_unit, # character varying, default: NULL::character varying
        oper_sched_id, # integer, default: NULL::integer
        usage_zone_id, # integer, default: NULL::integer
        building_unit_id, # integer, default: NULL::integer
        )
