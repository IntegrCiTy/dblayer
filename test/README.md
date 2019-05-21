# Testing the DBLayer package


## About

This directory contains tests for the IntegrCiTY database layer.


## Prerequisites

For testing package `dblayer`, the following additional Python packages have to be installed:

 * [pandapower](https://pandapower.readthedocs.io/en/v2.0.1/index.html)
 * [pandathermal](https://github.com/IntegrCiTy/PandaThermal)
 * [pandangas](https://github.com/IntegrCiTy/PandaNGas)


Furthermore, a working **PostgreSQL** implementation of the [3DCityDB](https://www.3dcitydb.org) has to be installed, including its [extensions](https://github.com/gioagu/3dcitydb_ade), the **Energy ADE**, the **Utility Network ADE**, the **Scenario ADE** and the **Simulation Package**.
For the tests to work properly, file `test_dblayer.py` has to be adapted to the configuration of this database:
 * Adapt the `PostgreSQLConnectionInfo` in function `fix_connect()` your actual  database implementation. By *default*, it is assumed that the database name is `testdb`, that it is installed locally (and accessible via standard port 5432) and that it can be accessed by a user called `postgres` (with password `postgres`).
 * Adapt the *spatial reference ID* (SRID) in function `fix_srid()` your actual  database implementation. By *default*, it is assumed that the SRID is `2056`.



## Testing the package

The [pytest package](https://docs.pytest.org) is used for testing the DBLayer package.
After installation of the DBLayer package, open a command terminal, change to the `test` directory and type the following:
```
pytest test_dblayer.py
```
***NOTE***: When running the test, function `sim_pkg.cleanup_schema()` is called at the beginning. This will erase all previously stored data from the database.