# Setting up the extended 3DCityDB

Script `setup_extended_3dcitydb.sh` automates the installation of the extended 3DCityDB on Linux.

## Prerequisites

The following software needs to be installed before running the script:
 * [docker](https://docs.docker.com/install)
 * PostgreSql (e.g., via `sudo apt-get install postgresql postgresql-client`)
 * git (e.g., via `sudo apt-get install git`)

## Customized installation process

The installation process can be customized by defining the following variables in the terminal prior to execution:
 * `CONTAINERNAME`: name for the 3DCityDB PostGIS Docker container (default: citydb-container)
 * `CONTAINERTAG`: tag of the 3DCityDB PostGIS Docker container (default: none)
 * `PORT`: port for the 3DCityDB PostGIS Docker container to listen on (default: 5432)
 * `DBUSER`: user name for the 3DCityDB (default: postgres)
 * `DBPASSWORD`: password for the 3DCityDB (default: postgres)
 * `DBNAME`: database name for the 3DCityDB (default: citydb)
 * `SRID`: ID of the spatial reference system of the 3DCityDB (default: 4326)
 * `SRSNAME`: name of the spatial reference system to use for the 3DCityDB (default: urn:ogc:def:crs:EPSG::4326)
 * `PGBIN`: path to binary `psql` (default: /usr/bin).

## Example

The following example shows how the required configuration and installation procedure for running the tests:
```shell
export DBNAME=testdb
export CONTAINERTAG=:v3.3.1

./setup_extended_3dcitydb.sh
```

