#!/bin/sh

# Name for the 3DCityDB PostGIS Docker container (default=citydb-container).
CONTAINERNAME=${CONTAINERNAME:-citydb-container}

# Tag of the 3DCityDB PostGIS Docker container (default=None).
CONTAINERTAG=${CONTAINERTAG:-}

# Port for the 3DCityDB PostGIS Docker container to listen on (default=5432).
PORT=${PORT:-5432}

# Username for the 3DCityDB (default=postgres).
DBUSER=${DBUSER:-postgres}

# Password for the 3DCityDB (default=postgres).
DBPASSWORD=${DBPASSWORD:-postgres}

# Database name for the 3DCityDB (default=citydb).
DBNAME=${DBNAME:-citydb}

# SRID of the spatial reference system of the 3DCityDB (default=4326).
SRID=${SRID:-4326}

# Name of the spatial reference system to use for the 3DCityDB (default=urn:ogc:def:crs:EPSG::4326).
SRSNAME=${SRSNAME:-urn:ogc:def:crs:EPSG::4326}

# Path to binary "psql" (default=/usr/bin).
PGBIN=${PGBIN:-/usr/bin}


# Deploy 3DCityDB as Docker container.
docker run -dit --name "$CONTAINERNAME" \
    -p $PORT:5432 \
    -e "POSTGRES_USER=$DBUSER" \
    -e "POSTGRES_PASSWORD=$DBPASSWORD" \
    -e "CITYDBNAME=$DBNAME" \
    -e "SRID=$SRID" \
    -e "SRSNAME=$SRSNAME" \
    tumgis/3dcitydb-postgis"$CONTAINERTAG"


# Set password for database as environment variable.
export PGPASSWORD=$DBPASSWORD

# Wait until Docker container is ready and adapt search path of 3DCityDB.
until "$PGBIN/psql" -h localhost -p $PORT -d $DBNAME -U $DBUSER -c "ALTER DATABASE ${DBNAME} SET search_path TO citydb, citydb_pkg, public"
do
    echo "Waiting for 3DCityDB container..."
    sleep 10
done


# Retrieve and install 3D City Database Utilities Package (revision 5d365ba).
git clone https://github.com/gioagu/3dcitydb_utilities.git
cd 3dcitydb_utilities
git checkout 5d365ba
"$PGBIN/psql" -h localhost -p $PORT -d $DBNAME -U $DBUSER -f "INSTALL_citydb_utilities.sql"
cd ..


# Retrieve and install 3D City Database Metadata Module (revision 221e886).
git clone https://github.com/gioagu/3dcitydb_metadata_module.git
cd 3dcitydb_metadata_module
git checkout 221e886
"$PGBIN/psql" -h localhost -p $PORT -d $DBNAME -U $DBUSER -f "INSTALL_Metadata_module.sql"
cd ..


# Retrieve and install the CityGML Energy ADE (revision 4074ae7).
git clone https://github.com/gioagu/3dcitydb_energy_ade.git
cd 3dcitydb_energy_ade
git checkout 4074ae7
"$PGBIN/psql" -h localhost -p $PORT -d $DBNAME -U $DBUSER -f "INSTALL_Energy_ADE.sql"
cd ..


# Retrieve and install the CityGML Utility Network ADE (revision 6878ab0).
git clone https://github.com/gioagu/3dcitydb_utility_network_ade.git
cd 3dcitydb_utility_network_ade
git checkout 6878ab0
"$PGBIN/psql" -h localhost -p $PORT -d $DBNAME -U $DBUSER -f "INSTALL_Utility_Network_ADE.sql"
cd ..


# Retrieve and install the CityGML Scenario ADE (revision 954cf0b).
git clone https://github.com/gioagu/3dcitydb_scenario_ade.git
cd 3dcitydb_scenario_ade
git checkout 954cf0b
"$PGBIN/psql" -h localhost -p $PORT -d $DBNAME -U $DBUSER -f "INSTALL_Scenario_ADE.sql"
cd ..


# Retrieve and install the Simulation Package (revision a7e40bc).
git clone https://github.com/gioagu/3dcitydb_simulation_pkg.git
cd 3dcitydb_simulation_pkg
git checkout a7e40bc
"$PGBIN/psql" -h localhost -p $PORT -d $DBNAME -U $DBUSER -f "INSTALL_Simulation_PKG.sql"
cd ..
