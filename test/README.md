# Testing the OBNL Scenario Package


## About

This directory contains tests for the IntegrCiTY database layer:
- `test_scenario.py`: tests the basic functionality of the package to represent scenarios  (including persistency with JSON files)
- `test_scenario_db.py`: tests the database persistency


## Prerequisites

For testing the basic functionality, install the [DBLayer Package](https://github.com/IntegrCiTy/dblayer). 

For testing the database persistency, the following prerequisites apply:
- A working implementation of the [CityGML 3D City Database](http://)  plus the [Energy ADE](http://), [Network Utility ADE](http://), [Scenario ADE](http://) and the [Simulation Package](http://) needs to be available (PostgreSQL versions).
- Adapt the `PostgreSQLConnectionInfo` in file `test_scenario_db.py` to your actual  database implementation. By *default*, it is assumed that the database name is `testdb`, that it is installed locally (and accessible via standard port 5432) and that it can be accessed by a user called `postgres` (with password `postgres`).


## Testing the package

For testing the DBLayer Package, open a command terminal, change to the `test` directory and type the follwing:
```
python test_scenario.py
python test_scenario_db.py
```
***NOTE***: When running the test for the database persistency (script `test_scenario_db.py`), function `sim_pkg.cleanup_schema()` is called at the beginning. This will erase all previously stored data from the database.