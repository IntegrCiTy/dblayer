# Testing the DBLayer package


## About

This directory contains tests for the IntegrCiTY database layer.


## Prerequisites

For testing the basic functionality, install the [DBLayer Package](https://github.com/IntegrCiTy/dblayer). 

For testing the database persistence, the following prerequisites apply:
- A working implementation of the [CityGML 3D City Database](http://)  plus the [Energy ADE](http://), [Network Utility ADE](http://), [Scenario ADE](http://) and the [Simulation Package](http://) needs to be available (PostgreSQL versions).
- Adapt the `PostgreSQLConnectionInfo` in function `fix_connect()` in file `test_dblayer.py` to your actual  database implementation. By *default*, it is assumed that the database name is `testdb`, that it is installed locally (and accessible via standard port 5432) and that it can be accessed by a user called `postgres` (with password `postgres`).


## Testing the package

The [pytest package](https://docs.pytest.org) is used for testing the DBLayer package.
After installation of the DBLayer package, open a command terminal, change to the `test` directory and type the following:
```
pytest test_dblayer.py
```
***NOTE***: When running the test, function `sim_pkg.cleanup_schema()` is called at the beginning. This will erase all previously stored data from the database.