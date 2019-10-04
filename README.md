# The DBLayer Package - IntegrCiTy Data Access Layer

## About

Package `dblayer` implements the so-called a **data access layer** for the [IntegrCiTy](http://iese.heig-vd.ch/projets/integrcity) project.
It aims to provide a link between the worlds of 3D semantic city models and technical simulation models.

This includes:
* retrieving/storing scenario data from/to a database
* creating simulation models from information stored in a database
* retrieving/storing co-simulation setups from/to a database
* associating initial values and parameters of a simulator configuration with entries in the database and retrieving/storing the from/to the database


## Examples

Examples for using package DBLayer can be found in subdirectory `examples`.


## Installation and prerequisites

1. The basic functionality of the package (including access to PostgreSQL databases) can be installed from the command line:
```
   > pip install -r requirements.txt
   > python setup.py install
```
2. Install the [IntegrCiTy co-simulation deployment API (ictdeploy package)](https://github.com/IntegrCiTy/ictdeploy).
3. In addition, a working **PostgreSQL** implementation of the [3DCityDB](https://www.3dcitydb.org) has to be installed, including its [extensions](https://github.com/gioagu/3dcitydb_ade), the **Energy ADE**, the **Utility Network ADE**, the **Scenario ADE** and the **Simulation Package**.
Such a database setup is referred to as **extended 3DCityDB**.
See subfolder `scripts` for installation instructions.

***NOTE***: Consider to install the DBLayer package in a virtual environment (as suggested by the installation instructions for the ictdeploy package).

## Testing

Subfolder `test` contains extensive tests of the functionality provided by package `dblayer`.
