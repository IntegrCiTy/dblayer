# The DBLayer Package - IntegrCiTy Data Access Layer

## About

Package `dblayer` implements the so-called a **data access layer** for the [IntegrCiTy](http://iese.heig-vd.ch/projets/integrcity) project.
It aims to provide a link between the worlds of 3D semantic city models and technical simulation models.

This includes:
* retrieving/storing data from/to a database
* creating simulation models from information stored in a database
* retrieving/storing co-simulation setups from/to a database
* associating initial values and parameters of a simulator configuration with entries in the database and retrieving/storing them from/to the database


## Examples

Examples for using package DBLayer can be found in subdirectory `examples`.


## Installation and prerequisites

1. The basic functionality of the package (including access to PostgreSQL databases and the IntegrCiTy co-simulation platform [ZerOBNL](https://github.com/IntegrCiTy/zerobnl)) can be installed from the command line:
```
pip install -e git+https://github.com/IntegrCiTy/dblayer#egg=dblayer
```
2. In addition, a working **PostgreSQL** implementation of the [3DCityDB](https://www.3dcitydb.org) has to be installed, including its [extensions](https://github.com/gioagu/3dcitydb_ade), the **Energy ADE**, the **Utility Network ADE**, the **Scenario ADE** and the **Simulation Package**.
Such a database setup is referred to as **extended 3DCityDB**.
See subfolder `scripts` for installation instructions.

***NOTE***: Consider to install the DBLayer package in a virtual environment (as suggested by the installation instructions for the **zerobnl** package).

## Testing

Subfolder `test` contains extensive tests of the functionality provided by package `dblayer`.
Install and run `pytest` to run the tests.
```
pip install pytest
pytest
```
