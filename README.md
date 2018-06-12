# The DBLayer Package

## About

To run [OBNL](https://github.com/IntegrCiTy/obnl), the user has to provide a **co-simulation setup** to the [IntegrCiTy co-simulation deployment API](https://github.com/IntegrCiTy/ictdeploy), which defines the individual simulation nodes, the input and output variables of these nodes as well as the links between the input and output variables.

The **DBLayer package** provides a link between such co-simulation setups and a database.
This includes:
* retrieving/storing scenario data from/to a database
* retrieving/storing co-simulation setups from/to a database
* associating initial values and parameters of a simulator configuration with entries in the database and retrieving/storing the from/to the database


## Installation and prerequisites

1. The basic functionality of the package (including access to PostgreSQL databases) can be installed from the command line:
```
     > python setup.py install
```
2. Install the [IntegrCiTy co-simulation deployment API (ictdeploy package)](https://github.com/IntegrCiTy/ictdeploy).
3. In addition, a working **PostgreSQL** implementation of the [3DCityDB](https://www.3dcitydb.org) has to be installed, including its [extensions](https://github.com/gioagu/3dcitydb_ade), the **Energy ADE**, the **Utility Network ADE**, the **Scenario ADE** and the **Simulation Package**. Such a database setup is referred to as **extended 3DCityDB** below.

***NOTE***: Consider to install the DBLayer package in a virtual environment (as suggested by the installation instructions for the ictdeploy package).


## Overview

### Accessing the extended 3DCityDB

This section shows basic examples of how to interact with the 3DCityDB through the DBLayer package.
Its most basic functionality is to provide access to the database.
This is achieved through class `DBAccess`, which allows to connect to an instance of the extended 3DCityDB by calling function `connect_to_citydb` using an instance of `PostgreSQLConnectionInfo`:

```python
  from dblayer import *

  # Define connection parameters.
  connect = PostgreSQLConnectionInfo(
    user = 'postgres',
    pwd = 'postgres',
    host = 'localhost',
    port = '5432',
    dbname = 'testdb'
    )

  # Create access point.
  access = DBAccess()

  # Connect to database.
  access.connect_to_citydb( connect )
```

After a successful connection, class `DBAccess` offers several functions enabling a user-friendly interaction with the database.
For instance, an important feature is that the SQL functions of the extended 3DCityDB can be called to insert new objects.
The following code snippet demonstrates how a new heat pump object is inserted with a reference to the building it belongs to (e.g., with building ID 1122) using SQL function `insert_heat_pump`.
Finally, these changes are committed permanently to the database.

```python
  # Add a new entry to the databse using SQL function "insert_heat_pump".
  hp_id = access.add_citydb_object(
    insert_heat_pump,
    name = 'HEATPUMP_01',
    nom_effcy = 1.2,
    effcy_indicator = 'COP',
    inst_in_ctyobj_id = 1122
    )

  # Commit the changes to the database.
  access.commit_citydb_session()
```

In the context of creating co-simulation setups it is probably most important to have easy access to data already available in the database.
For this, the extended 3DCityDB provides in many cases convenient views.
The following example shows how this can be done in the case of heat pump data.
First, class `HeatPump` is associated with the view `citydb_view.nrg8_conv_system_heat_pump`.
This association is then used to refine conditions for querying the database.
Finally, function `get_citydb_objects` is called to retrieve data from the specified view with the specified query conditions.

```python
  # Map table "citydb_view.nrg8_conv_system_heat_pump" to Python class HeatPump.
  HeatPump = access.map_citydb_object_class(
    'HeatPump',
    schema = 'citydb_view',
    table_name = 'nrg8_conv_system_heat_pump'
    )

  # Use the attributes of class HeatPump to define query conditions.
  conditions = [
    HeatPump.name == 'HEATPUMP_01',
    HeatPump.nom_effcy == 1.2
    ]

  # Query the database using the conditions defined above.
  heatpumps = access.get_citydb_objects(
    'HeatPump',
    conditions = conditions
    )

  # Retrieve data from query result.
  effcy_ind = heatpumps[0].effcy_indicator
  heatpump_id = heatpumps[0].id
```


### Storing co-simulation setups.

For the following, consider that a co-simulation setup called `sim` has been defined with the help of the  [IntegrCiTy co-simulation deployment API](https://github.com/IntegrCiTy/ictdeploy):

```python
  from ictdeploy import Simulator

  # Create simulation setup.
  sim = ictdeploy.Simulator()

  # Add meta model.
  sim.edit.add_meta(
    name = 'BaseMeta',
    set_attrs = [ 'a' ],
    get_attrs = [ 'b' ]
    )

  # Add model based on meta model.
  sim.edit.add_model(
    name = 'BaseModel',
    meta = 'BaseMeta',
    image = 'integrcity/ict-simple',
    wrapper = os.path.join( 'tests', 'wrappers', 'base_wrap.py' ),
    command = None,
    files = [ os.path.join( 'tests', 'files_to_add', 'empty_file_for_testing_purpose.txt' ) ]
    )

  # Add node based on model.
  sim.edit.add_node(
    name = 'Base0',
    model = 'BaseModel',
    init_values = { 'c': 0.5 },
    is_first = True
    )

  # Add another node based on model.
  sim.edit.add_node(
     name = 'Base1',
     model = 'BaseModel',
     init_values = { 'c': 0.25 }
    )

  # Define links between nodes.
  sim.edit.add_link( get_node = 'Base0', get_attr = 'b', set_node = 'Base1', set_attr = 'a' )
  sim.edit.add_link( get_node = 'Base1', get_attr = 'b', set_node = 'Base0', set_attr = 'a' )

  # Define simulation groups and sequence.
  grp0 = sim.create_group( 'Base0' )
  grp1 = sim.create_group( 'Base1' )
  sim.create_sequence( grp0, grp1 )

  # Define simulation time steps.
  sim.create_steps( [60] * 10 )
```

Package DBLayer implements the mapping of the **Simulation Package** scheme to IntegrCiTy’s concepts for representing such a co-simulation setup, providing basically a persistence layer for co-simulation setups.
For storing co-simulation setups to the extended 3DCityDB, package DBLayer provides class `DBWriter`.
Upon connecting to the database, a co-simulation setup can be assigned a name and written to the database with the help of a single command.
Setting parameters `write_meta_models` and `write_models` to `False` indicates that a co-simulation setup already defining meta-model `MetaBase` and model `BaseModel` has been previously written to the same database (otherwise the corresponding parameters should be omitted).

```python
  # Create writer and connect to database.
  writer = DBWriter( connect )

  # Write co-simulation setup to database.
  writer.write_to_db(
    sim,
    'TestSim1',
    write_meta_models = False,
    write_models = False
  )
```

### Retrieving co-simulation setups

For reading co-simulation setups from the extended 3DCityDB, package DBLayer provides class `DBReader`.
Upon connecting to the database, a co-simulation setup stored in the database can be referred to by name and retrieved with the help of a single command.
In the example below, which simply reads back the co-simulation setup written in the previous example, the resulting object `sim_read` would be identical to object `sim` from above.

```python
  # Create reader and connect to database.
  reader = DBReader( connect )

  # Read co-simulation setup from database.
  sim_read = reader.read_from_db( 'TestSim1' )
```


### Associate co-simulation setups with 3DCityDB data

In the current IntegrCiTy toolchain, the association of co-simulation setups with 3DCityDB data happens first and foremost by using the available information to parametrize simulation models.
In the context of urban energy systems simulation, this comprises not only scalar model parameters (e.g., U-values for walls) but also time-series data as provided via the Energy ADE (e.g., electrical load profiles).

The rather trivial approach for such an association is to directly retrieve certain values (according to the example above) and setting them as initial values when defining the co-simulation setup.

However, package DBLayer and the Simulation Package also allow to persistently store associations with attributes of 3DCityDB objects and generic parameters.
This is demonstrated in the following pseudo code snippet, which basically extends the co-simulation setup shown above by defining an instance of class `AssociateCityDBObject` and assigning it to parameter `c` of node `Base0`.

```python
  # Define table and attribute (table column) name for association.
  table = 'citydb_view.nrg8_conv_system_heat_pump'
  attribute = 'nom_effcy'

  # Define association with the help of the object ID (table row).
  associate_object = AssociateCityDBObject(
    table_name = table,
    object_id = heatpump_id,
    column_name = attribute
    )

  # Link attribute "c" of "Base0" with the association.
  sim_assoc.edit.nodes.loc[ 'Base0' ].init_values[ 'c' ] = associate_object

  # Write the co-simulation setup to the database (storing the association).
  writer.write_to_db(
    sim_assoc,
    'TestSim2',
    write_meta_models = False,
    write_models = False
    )
```

Please note that in above example the resulting co-simulation graph object `sim_assoc` is **not valid to deploy an actual co-simulation** (because parameter `c` is not associated to a scalar or vector).
However, when writing the setup to the database, the association of parameter `c` with the corresponding table attribute is stored persistently.
Furthermore, **when reading this stored co-simulation setup from the database** (using class `DBReader`), the **association is automatically resolved**.
This means that parameter `c` in the resulting co-simulation setup would have the corresponding numerical value and the setup would be **valid to deploy an actual co-simulation**.
