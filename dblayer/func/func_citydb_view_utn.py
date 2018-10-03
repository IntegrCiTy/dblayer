from sqlalchemy.sql import func


def insert_feature_graph(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    ntw_feature_id = None,
    ntw_graph_id = None
    ):
    '''
    Define function call to insert feature graph into the database.
    '''
    return func.citydb_view.utn9_insert_feature_graph(
        id, # integer, default: NULL::integer
        gmlid, # character varying, default: NULL::character varying
        gmlid_codespace, # character varying, default: NULL::character varying
        name, # character varying, default: NULL::character varying
        name_codespace, # character varying, default: NULL::character varying
        description, # text, default: NULL::text
        ntw_feature_id, # integer, default: NULL::integer
        ntw_graph_id # integer, default: NULL::integer
        )


def insert_link_interfeature(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    direction = None,
    link_control = None,
    interfeature_link_type = None,
    start_node_id = None,
    end_node_id = None,
    feat_graph_id = None,
    ntw_graph_id = None,
    line_geom = None
    ):
    '''
    Define function call to insert inter-feature link into the database.
    '''
    return func.citydb_view.utn9_insert_link_interfeature(
        id, # integer, default: NULL::integer
        gmlid, # character varying, default: NULL::character varying
        gmlid_codespace, # character varying, default: NULL::character varying
        name, # character varying, default: NULL::character varying
        name_codespace, # character varying, default: NULL::character varying
        description, # text, default: NULL::text
        direction, # character, default: NULL::bpchar
        link_control, # character varying, default: NULL::character varying
        interfeature_link_type, # character varying, default: NULL::character varying
        start_node_id, # integer, default: NULL::integer
        end_node_id, # integer, default: NULL::integer
        feat_graph_id, # integer, default: NULL::integer
        ntw_graph_id, # integer, default: NULL::integer
        line_geom # geometry, default: NULL::geometry
        )


def insert_link_interior_feature(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    direction = None,
    link_control = None,
    start_node_id = None,
    end_node_id = None,
    feat_graph_id = None,
    line_geom = None
    ):
    '''
    Define function call to insert interior-feature link into the database.
    '''
    return func.citydb_view.utn9_insert_link_interior_feature(
        id, # integer DEFAULT NULL::integer
        gmlid, # character varying DEFAULT NULL::character varying
        gmlid_codespace, # character varying DEFAULT NULL::character varying
        name, # character varying DEFAULT NULL::character varying
        name_codespace, # character varying DEFAULT NULL::character varying
        description, # text DEFAULT NULL::text
        direction, # character DEFAULT NULL::bpchar
        link_control, # character varying DEFAULT NULL::character varying
        start_node_id, # integer DEFAULT NULL::integer
        end_node_id, # integer DEFAULT NULL::integer
        feat_graph_id, # integer DEFAULT NULL::integer
        line_geom # geometry DEFAULT NULL::geometry
        )


def insert_network(
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
    network_parent_id = None,
    network_root_id = None,
    class_name = None,
    function = None,
    usage = None,
    commodity_id = None
    ):
    '''
    Define function call to insert network into the database.
    '''
    return func.citydb_view.utn9_insert_network(
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
        network_parent_id, # integer, default: NULL::integer
        network_root_id, # integer, default: NULL::integer
        class_name, # character varying, default: NULL::character varying
        function, # character varying, default: NULL::character varying
        usage, # character varying, default: NULL::character varying
        commodity_id, # integer, default: NULL::integer
        )


def insert_network_graph(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    network_id = None
    ):
    '''
    Define function call to insert network graph into the database.
    '''
    return func.citydb_view.utn9_insert_network_graph(
        id, # integer, default: NULL::integer
        gmlid, # character varying, default: NULL::character varying
        gmlid_codespace, # character varying, default: NULL::character varying
        name, # character varying, default: NULL::character varying
        name_codespace, # character varying, default: NULL::character varying
        description, # text, default: NULL::text
        network_id, # integer, default: NULL::integer
        )


def insert_node(
    id = None,
    gmlid = None,
    gmlid_codespace = None,
    name = None,
    name_codespace = None,
    description = None,
    type = None,
    connection_signature = None,
    link_control = None,
    feat_graph_id = None,
    point_geom = None
    ):
    '''
    Define function call to insert node into the database.
    '''
    return func.citydb_view.utn9_insert_node(
        id, # integer, default: NULL::integer
        gmlid, # character varying, default: NULL::character varying
        gmlid_codespace, # character varying, default: NULL::character varying
        name, # character varying, default: NULL::character varying
        name_codespace, # character varying, default: NULL::character varying
        description, # text, default: NULL::text
        type, # character varying, default: NULL::character varying
        connection_signature, # character varying, default: NULL::character varying
        link_control, # character varying, default: NULL::character varying
        feat_graph_id, # integer, default: NULL::integer
        point_geom, # geometry, default: NULL::geometry
        )


def insert_ntw_feat_distrib_elem_cable(
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
    ntw_feature_parent_id = None,
    ntw_feature_root_id = None,
    class_name = None,
    function = None,
    usage = None,
    year_of_construction = None,
    status = None,
    location_quality = None,
    elevation_quality = None,
    cityobject_id = None,
    prot_element_id = None,
    geom = None,
    function_of_line = None,
    is_transmission = None,
    is_communication = None,
    cross_section = None,
    cross_section_unit = None
    ):
    '''
    Define function call to insert electrical cable into the database.
    '''
    return func.citydb_view.utn9_insert_ntw_feat_distrib_elem_cable(
        id, # integer, default:: NULL::integer
        gmlid, # character varying, default:: NULL::character varying
        gmlid_codespace, # character varying, default:: NULL::character varying
        name, # character varying, default:: NULL::character varying
        name_codespace, # character varying, default:: NULL::character varying
        description, # character varying, default:: NULL::character varying
        envelope, # geometry, default:: NULL::geometry
        creation_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        termination_date, # timestamp with time zone, default:: NULL::timestamp with time zone
        relative_to_terrain, # character varying, default: NULL::character varying
        relative_to_water, # character varying, default: NULL::character varying
        last_modification_date, # timestamp with time zone, default: NULL::timestamp with time zone
        updating_person, # character varying, default: NULL::character varying
        reason_for_update, # character varying, default: NULL::character varying
        lineage, # character varying, default: NULL::character varying
        ntw_feature_parent_id, # integer, default: NULL::integer
        ntw_feature_root_id, # integer, default: NULL::integer
        class_name, # character varying, default: NULL::character varying
        function, # character varying, default: NULL::character varying
        usage, # character varying, default: NULL::character varying
        year_of_construction, # date, default: NULL::date
        status, # character varying, default: NULL::character varying
        location_quality, # character varying, default: NULL::character varying
        elevation_quality, # character varying, default: NULL::character varying
        cityobject_id, # integer, default: NULL::integer
        prot_element_id, # integer, default: NULL::integer
        geom, # geometry, default: NULL::geometry
        function_of_line, # character varying, default: NULL::character varying
        is_transmission, # numeric, default: NULL::numeric
        is_communication, # numeric, default: NULL::numeric
        cross_section, # numeric, default: NULL::numeric
        cross_section_unit # character varying, default: NULL::character varying
        )


def insert_ntw_feat_device_tech(
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
    ntw_feature_parent_id = None,
    ntw_feature_root_id = None,
    class_name = None,
    function = None,
    usage = None,
    year_of_construction = None,
    status = None,
    location_quality = None,
    elevation_quality = None,
    cityobject_id = None,
    prot_element_id = None,
    geom = None
    ):
    '''
    Define function call to insert tech device into the database.
    '''
    return func.citydb_view.utn9_insert_ntw_feat_device_tech(
        id, # integer, default: NULL::integer,
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
        ntw_feature_parent_id, # integer, default: NULL::integer
        ntw_feature_root_id, # integer, default: NULL::integer
        class_name, # character varying, default: NULL::character varying
        function, # character varying, default: NULL::character varying
        usage, # character varying, default: NULL::character varying
        year_of_construction, # date, default: NULL::date
        status, # character varying, default: NULL::character varying
        location_quality, # character varying, default: NULL::character varying
        elevation_quality, # character varying, default: NULL::character varying
        cityobject_id, # integer, default: NULL::integer
        prot_element_id, # integer, default: NULL::integer
        geom, # geometry, default: NULL::geometry
        )


def insert_ntw_feat_simple_funct_elem(
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
    ntw_feature_parent_id = None,
    ntw_feature_root_id = None,
    class_name = None,
    function = None,
    usage = None,
    year_of_construction = None,
    status = None,
    location_quality = None,
    elevation_quality = None,
    cityobject_id = None,
    prot_element_id = None,
    geom = None
    ):
    '''
    Define function call to insert simple functional element into the database.
    '''
    return func.citydb_view.utn9_insert_ntw_feat_simple_funct_elem(
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
        ntw_feature_parent_id, # integer, default: NULL::integer
        ntw_feature_root_id, # integer, default: NULL::integer
        class_name, # character varying, default: NULL::character varying
        function, # character varying, default: NULL::character varying
        usage, # character varying, default: NULL::character varying
        year_of_construction, # date, default: NULL::date
        status, # character varying, default: NULL::character varying
        location_quality, # character varying, default: NULL::character varying
        elevation_quality, # character varying, default: NULL::character varying
        cityobject_id, # integer, default: NULL::integer
        prot_element_id, # integer, default: NULL::integer
        geom, # geometry, default: NULL::geometry
        )


def insert_ntw_feat_complex_funct_elem(
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
    ntw_feature_parent_id = None,
    ntw_feature_root_id = None,
    class_name = None,
    function = None,
    usage = None,
    year_of_construction = None,
    status = None,
    location_quality = None,
    elevation_quality = None,
    cityobject_id = None,
    prot_element_id = None,
    geom = None
    ) :
    '''
    Define function call to insert complex functional element into the database.
    '''
    return func.citydb_view.utn9_insert_ntw_feat_complex_funct_elem(
        id, # integer, default: NULL::integer,
        gmlid, # character varying, default: NULL::character varying,
        gmlid_codespace, # character varying, default: NULL::character varying,
        name, # character varying, default: NULL::character varying,
        name_codespace, # character varying, default: NULL::character varying,
        description, # character varying, default: NULL::character varying,
        envelope, # geometry, default: NULL::geometry,
        creation_date, # timestamp with time zone, default: NULL::timestamp with time zone,
        termination_date, # timestamp with time zone, default: NULL::timestamp with time zone,
        relative_to_terrain, # character varying, default: NULL::character varying,
        relative_to_water, # character varying, default: NULL::character varying,
        last_modification_date, # timestamp with time zone, default: NULL::timestamp with time zone,
        updating_person, # character varying, default: NULL::character varying,
        reason_for_update, # character varying, default: NULL::character varying,
        lineage, # character varying, default: NULL::character varying,
        ntw_feature_parent_id, # integer, default: NULL::integer,
        ntw_feature_root_id, # integer, default: NULL::integer,
        class_name, # character varying, default: NULL::character varying,
        function, # character varying, default: NULL::character varying,
        usage, # character varying, default: NULL::character varying,
        year_of_construction, # date, default: NULL::date,
        status, # character varying, default: NULL::character varying,
        location_quality, # character varying, default: NULL::character varying,
        elevation_quality, # character varying, default: NULL::character varying,
        cityobject_id, # integer, default: NULL::integer,
        prot_element_id, # integer, default: NULL::integer,
        geom # geometry, default: NULL::geometry
        )


def insert_ntw_feat_term_elem(
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
    ntw_feature_parent_id = None,
    ntw_feature_root_id = None,
    class_name = None,
    function = None,
    usage = None,
    year_of_construction = None,
    status = None,
    location_quality = None,
    elevation_quality = None,
    cityobject_id = None,
    prot_element_id = None,
    geom = None
    ):
    '''
    Define function call to insert terminal element into the database.
    '''
    return func.citydb_view.utn9_insert_ntw_feat_term_elem(
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
        ntw_feature_parent_id, # integer, default: NULL::integer
        ntw_feature_root_id, # integer, default: NULL::integer
        class_name, # character varying, default: NULL::character varying
        function, # character varying, default: NULL::character varying
        usage, # character varying, default: NULL::character varying
        year_of_construction, # date, default: NULL::date
        status, # character varying, default: NULL::character varying
        location_quality, # character varying, default: NULL::character varying
        elevation_quality, # character varying, default: NULL::character varying
        cityobject_id, # integer, default: NULL::integer
        prot_element_id, # integer, default: NULL::integer
        geom # geometry, default: NULL::geometry
        )


def insert_network_to_network_feature(
    network_id,
    network_feature_id
    ):
    '''
    Insert association between network and network feature.
    '''
    return func.citydb_pkg.utn9_insert_network_to_network_feature(
        network_id, # integer
        network_feature_id # integer
        )
