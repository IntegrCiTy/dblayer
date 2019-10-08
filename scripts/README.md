# Installing the extended 3DCityDB on Linux

Script `setup_extended_3dcitydb.sh` automates the installation of the extended 3DCityDB on Linux.

## Prerequisites

The following software needs to be installed before running the script:
 * [docker](https://docs.docker.com/install)
 * PostgreSql (e.g., via `sudo apt-get install postgresql postgresql-client`)
 * git (e.g., via `sudo apt-get install git`)

## Customized installation process

The installation process can be customized by defining the following variables in the terminal prior to execution:
 * `CONTAINERNAME`: name for the 3DCityDB PostGIS Docker container (default: :v3.3.1)
 * `CONTAINERTAG`: tag of the 3DCityDB PostGIS Docker container (default: none)
 * `PORT`: port for the 3DCityDB PostGIS Docker container to listen on (default: 5432)
 * `DBUSER`: user name for the 3DCityDB (default: postgres)
 * `DBPASSWORD`: password for the 3DCityDB (default: postgres)
 * `DBNAME`: database name for the 3DCityDB (default: citydb)
 * `SRID`: ID of the spatial reference system of the 3DCityDB (default: 4326)
 * `SRSNAME`: name of the spatial reference system to use for the 3DCityDB (default: urn:ogc:def:crs:EPSG::4326)
 * `PGBIN`: path to binary `psql` (default: /usr/bin)

## Running the script

The following example shows how to execute the script with non-default values for `DBNAME` and `CONTAINERTAG`:
```shell
export DBNAME=testdb
export CONTAINERTAG=:v4.0.1

./setup_extended_3dcitydb.sh
```

# Installing the extended 3DCityDB on Windows

Script `setup_extended_3dcitydb.bat` automates the installation of the extended 3DCityDB on Windows.

## Prerequisites

The following software needs to be installed before running the script:
 * [docker](https://docs.docker.com/install)
 * [PostgreSql](https://www.postgresql.org)
 * [git](https://gitforwindows.org/)

## Customized installation process

The installation process can be customized by changing the following parameters at the beginning of the script prior to execution:
 * `CONTAINERNAME`: name for the 3DCityDB PostGIS Docker container (default: citydb-container)
 * `CONTAINERTAG`: tag of the 3DCityDB PostGIS Docker container (default: :v3.3.1)
 * `PORT`: port for the 3DCityDB PostGIS Docker container to listen on (default: 5432)
 * `DBUSER`: user name for the 3DCityDB (default: postgres)
 * `DBPASSWORD`: password for the 3DCityDB (default: postgres)
 * `DBNAME`: database name for the 3DCityDB (default: citydb)
 * `SRID`: ID of the spatial reference system of the 3DCityDB (default: 4326)
 * `SRSNAME`: name of the spatial reference system to use for the 3DCityDB (default: urn:ogc:def:crs:EPSG::4326)
 * `PGBIN`: path to binary `psql.exe` (default: C:\Tools\PostgreSQL\9.4\bin)
 * `GITBIN`: path to binary `git.exe` (default: C:\Program Files\Git\bin)

## Running the script

Run the script either by double-clicking it in the file explorer or calling it from the command line.
