# The DBLayer Package

## About

To run [OBNL](https://github.com/IntegrCiTy/obnl), the user has to provide a **simulator configuration** to the [IntegrCiTy co-simulation deployment API](https://github.com/IntegrCiTy/ictdeploy), which defines the individual simulation nodes, the input and output variables of these nodes as well as the links between the input and output variables.

The **DBLayer package** provides a link between such simulator configurations and a database. 
This includes:
* retrieving/storing simulation configurations from/to a database
* associating initial values and parameters of a simulator configuration with entries in the database and retrieving/storing the from/to the database


## Installation and prerequisites

1. The basic functionality of the package (including access to PostgreSQL databases) can be installed from the command line:
```
     > python setup.py install
```
2. Install the [IntegrCiTy co-simulation deployment API (ictdeploy package)](https://github.com/IntegrCiTy/ictdeploy).
***NOTE***: Consider to install the DBLayer package in a virtual environment (as suggested by the installation instructions for the ictdeploy package).
3. In addition, a working implementation of the [CityGML 3D City Database](http://)  plus the [Energy ADE](http://), [Network Utility ADE](http://), [Scenario ADE](http://) and the [Simulation Package](http://) needs to be available (PostgreSQL versions).


## Simulator configuration persistence

Simulator configurations can written to and read from a database that implements the CityGML 3D City Database Simulation Package (PostgreSQL/PostGIS).

### Database connection

The first step is to define the connection parameters for the PostgreSQL database.
This can be done via an instance of `PostgreSQLConnectionInfo`:
```python
from dblayer import *

connect = PostgreSQLConnectionInfo( 
    user = 'postgres',
    pwd = 'postgres',
    host = 'localhost', 
    port = '5432', 
    dbname = 'testdb'
    )
```

### Storing simulator configurations

Storing a simulator configuration to the database is done via the `DBWriter` class:
```python
sim = ictdeploy.Simulator()

# ... define simulator configuration ...

writer = DBWriter( sim )
writer.write_to_db( 'TestSim', connect )
```

### Retrieving simulator configurations

Similarly, retrieving a simulator configuration from the database is done with the help of the `DBReader` class:
```python
reader = DBReader()
sim = reader.read_from_db( 'TestSim', connect )
```

### Associating database entries

*To be done ...*