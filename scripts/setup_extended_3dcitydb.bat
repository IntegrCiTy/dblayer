@ECHO OFF

REM Name for the 3DCityDB PostGIS Docker container.
SET CONTAINERNAME=citydb-container

REM Tag of the 3DCityDB PostGIS Docker container.
SET CONTAINERTAG=:v3.3.1

REM Port for the 3DCityDB PostGIS Docker container to listen on.
SET PORT=5432

REM Username for the 3DCityDB.
SET DBUSER=postgres

REM Password for the 3DCityDB.
SET DBPASSWORD=postgres

REM Database name for the 3DCityDB.
SET DBNAME=testdb

REM SRID of the spatial reference system of the 3DCityDB.
SET SRID=4326

REM Name of the spatial reference system to use for the 3DCityDB (default=urn:ogc:def:crs:EPSG::4326).
SET SRSNAME=urn:ogc:def:crs:EPSG::4326

REM Path to directory containing binary "psql.exe".
SET PGBIN=C:\Tools\PostgreSQL\9.4\bin

REM Path to directory containing binary "git.exe".
SET GITBIN=C:\Program Files\Git\bin


REM Deploy 3DCityDB as Docker container.
docker run -dit --name "%CONTAINERNAME%" ^
 -p %PORT%:5432 ^
 -e "POSTGRES_USER=%DBUSER%" ^
 -e "POSTGRES_PASSWORD=%DBPASSWORD%" ^
 -e "CITYDBNAME=%DBNAME%" ^
 -e "SRID=%SRID%" ^
 -e "SRSNAME=%SRSNAME%" ^
 tumgis/3dcitydb-postgis"%CONTAINERTAG%

REM Check if running the container succeeded. If not, skip the remaine
IF NOT %ERRORLEVEL% == 0 GOTO :EOF


REM Set password for database as environment variable.
SET PGPASSWORD=%DBPASSWORD%


REM Wait until Docker container is ready and adapt search path of 3DCityDB.
:LOOP_START
"%PGBIN%\psql.exe" -h localhost -p %PORT% -d %DBNAME% -U %DBUSER% -c "ALTER DATABASE %DBNAME% SET search_path TO citydb, citydb_pkg, public"
IF NOT %ERRORLEVEL% == 0 (
   ECHO PostgreSQL server not yet running ...
   TIMEOUT /T 5 /NOBREAK
   GOTO :LOOP_START
)

REM Retrieve and install 3D City Database Utilities Package (revision 5d365ba).
"%GITBIN%\git.exe" clone https://github.com/gioagu/3dcitydb_utilities.git
cd 3dcitydb_utilities
"%GITBIN%\git.exe" checkout 5d365ba --quiet
"%PGBIN%\psql.exe" -h localhost -p %PORT% -d %DBNAME% -U %DBUSER% -f "INSTALL_citydb_utilities.sql"
cd ..


REM Retrieve and install 3D City Database Metadata Module (revision 221e886).
"%GITBIN%\git.exe" clone https://github.com/gioagu/3dcitydb_metadata_module.git
cd 3dcitydb_metadata_module
"%GITBIN%\git.exe" checkout 221e886 --quiet
"%PGBIN%\psql.exe" -h localhost -p %PORT% -d %DBNAME% -U %DBUSER% -f "INSTALL_Metadata_module.sql"
cd ..


REM Retrieve and install the CityGML Energy ADE (revision 4074ae7).
"%GITBIN%\git.exe" clone https://github.com/gioagu/3dcitydb_energy_ade.git
cd 3dcitydb_energy_ade
"%GITBIN%\git.exe" checkout 4074ae7 --quiet
"%PGBIN%\psql.exe" -h localhost -p %PORT% -d %DBNAME% -U %DBUSER% -f "INSTALL_Energy_ADE.sql"
cd ..


REM Retrieve and install the CityGML Utility Network ADE (revision 6878ab0).
"%GITBIN%\git.exe" clone https://github.com/gioagu/3dcitydb_utility_network_ade.git
cd 3dcitydb_utility_network_ade
"%GITBIN%\git.exe" checkout 6878ab0 --quiet
"%PGBIN%\psql.exe" -h localhost -p %PORT% -d %DBNAME% -U %DBUSER% -f "INSTALL_Utility_Network_ADE.sql"
cd ..


REM Retrieve and install the CityGML Scenario ADE (revision 954cf0b).
"%GITBIN%\git.exe" clone https://github.com/gioagu/3dcitydb_scenario_ade.git
cd 3dcitydb_scenario_ade
"%GITBIN%\git.exe" checkout 954cf0b --quiet
"%PGBIN%\psql.exe" -h localhost -p %PORT% -d %DBNAME% -U %DBUSER% -f "INSTALL_Scenario_ADE.sql"
cd ..


REM Retrieve and install the Simulation Package (revision a7e40bc).
"%GITBIN%\git.exe" clone https://github.com/gioagu/3dcitydb_simulation_pkg.git
cd 3dcitydb_simulation_pkg
"%GITBIN%\git.exe" checkout a7e40bc --quiet
"%PGBIN%\psql.exe" -h localhost -p %PORT% -d %DBNAME% -U %DBUSER% -f "INSTALL_Simulation_PKG.sql"
cd ..
