# The DBLayer Package

## About

To run [OBNL](https://github.com/IntegrCiTy/obnl), the user has to provide a **scenario** to the [IntegrCiTy co-simulation deployment API](https://github.com/IntegrCiTy/ictdeploy), which defines the individual simulation nodes, the input and output variables of these nodes as well as the links between the input and output variables.
The **DBLayer Package** intends to provide an object-oriented interface for creating scenarios for OBNL simulations and for storing/retrieving them to/from a database.


## Installation and prerequisites

1. The basic functionality of the package (including access to PostgreSQL databases) can be installed from the command line:
```
     > python setup.py install
```
2. Install the [IntegrCiTy co-simulation deployment API (ictdeploy package)](https://github.com/IntegrCiTy/ictdeploy).
***NOTE***: Consider to install the DBLayer package in a virtual environment (as suggested by the installation instructions for the ictdeploy package).
3. In addition, a working implementation of the [CityGML 3D City Database](http://)  plus the [Energy ADE](http://), [Network Utility ADE](http://), [Scenario ADE](http://) and the [Simulation Package](http://) needs to be available (PostgreSQL versions).


## Using the Scenario Package

### Basic Usage: Defining a Scenario

The Scenario Package represents all the relevant parts of a scenario as individual objects, using for example instances of class `Scenario`, class `Node` or class `Link`.
The definition of a scenario typically starts with an instance of class `Scenario`, which serves as a container for all other objects (nodes, links, etc.). In the following, a scenario called `TestScenario` is used:
```python
from scenario import *

scenario = Scenario( 'TestScenario' )
```
In the next step, nodes should be added to the scenario and for each node the input and output variables should be defined.
In the following, the scenario's `create_and_add_node` function is used for this purpose:
```python
scenario.create_and_add_node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
scenario.create_and_add_node( 'B', output_variable_names = [ 'tb' ] )
scenario.create_and_add_node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )
```
The lines above create three nodes:
- Node `A` has one input variable (called `seta`) and one output variable (called `ta`).
- Node `B` has no input variables but one output variable (called `tb`).
- Node `C` has two input variables (called `t1` and `t2`) but no output variables.

Finally, links between the nodes' input and output varaiables can be defined.
A link may connect a single output variable from one node (`from_node`) to a single input variable from another node (`to_node`).
This can be done with the help of the scenario's `create_and_add_link` function, which takes the nodes' and variables' names as input:
```python
scenario.create_and_add_link( 'l1', from_node = 'A', output_variable_name = 'ta', to_node = 'C', input_variable_name = 't1' )
scenario.create_and_add_link( 'l2', from_node = 'B', output_variable_name = 'tb', to_node = 'C', input_variable_name = 't2' )
scenario.create_and_add_link( 'l3', from_node = 'C', output_variable_name = 'setc', to_node = 'A', input_variable_name = 'seta' )
```
The lines above create three links:
- Link `l1` connects output variable `ta` from node `A` to the input variable `t1` of node `C`.
- Link `l2` connects output variable `tb` from node `B` to the input variable `t2` of node `C`.
- Link `l3` connects output variable `setc` from node `C` to the input variable `seta` of node `A`.

All together, the full Python code to define the scenario would look like this:
```python
from scenario import *

scenario = Scenario( 'TestScenario' )

scenario.create_and_add_node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
scenario.create_and_add_node( 'B', output_variable_names = [ 'tb' ] )
scenario.create_and_add_node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )

scenario.create_and_add_link( 'l1', from_node = 'A', output_variable_name = 'ta', to_node = 'C', input_variable_name = 't1' )
scenario.create_and_add_link( 'l2', from_node = 'B', output_variable_name = 'tb', to_node = 'C', input_variable_name = 't2' )
scenario.create_and_add_link( 'l3', from_node = 'C', output_variable_name = 'setc', to_node = 'A', input_variable_name = 'seta' )
```

#### Alternative ways of defining the scenario

The example above uses the functions `create_and_add_node` and `create_and_add_link` to create nodes and links and add them to the scenario.
This is all done by refering to these nodes and links using their names via the scenario, without handling the actual objects.
However, it is also possible to define nodes and links as individual objects and add them to scenario later on.
This is done in the follwing example, which creates the same scenario as in the previous example.

```python
from scenario import *

nodeA = Node( 'A', input_variable_names = [ 'seta' ], output_variable_names = [ 'ta' ] )
nodeB = Node( 'B', output_variable_names = [ 'tb' ] )
nodeC = Node( 'C', input_variable_names = [ 't1', 't2' ], output_variable_names = [ 'setc' ] )

link1 = Link( 'l1', from_node = nodeA, output_variable_name = 'ta', to_node = nodeC, input_variable_name = 't1' )
link2 = Link( 'l2', from_node = nodeB, output_variable_name = 'tb', to_node = nodeC, input_variable_name = 't2' )
link3 = Link( 'l3', from_node = nodeC, output_variable_name = 'setc', to_node = nodeA, input_variable_name = 'seta' )

scenario = Scenario( 'TestScenario' )

scenario.add_node( nodeA )
scenario.add_node( nodeB )
scenario.add_node( nodeC )

scenario.add_link( link1 )
scenario.add_link( link2 )
scenario.add_link( link3 )
```

### Translating a scenario to/from a simulation graph

***TODO***: Explain how to link with ictdeploy package ...


### Scenario Persistency: JSON Files

Scenarios can written to and read from JSON files.
This is done in a way that is compatible with the scenario input files required by the OBNL core.

For instance, saving a scenario to a JSON file is done with the help of the `dump_to_json_file` function:
```python
from scenario.json import *

dump_to_json_file(
    scenario,
    file_name = 'json.txt'
    )
```
Similarly, reading a scenario from a JSON file is done via the `read_from_json_file` function:
```python
from scenario.json import *

scenario = read_from_json_file( 
    file_name = 'json.txt',
    scenario_name = 'TestScenario'
    )
```

### Scenario Persistency: CityGML 3D City Database Simulation Package

Scenarios can written to and read from a database that implements the CityGML 3D City Database Simulation Package (PostgreSQL/PostGIS).

The first step is to define the connection parameters for the PostgreSQL database.
This can be done via an instance of `PostgreSQLConnectionInfo`:
```python
from scenario.db import *

connect = PostgreSQLConnectionInfo( 
    user = 'postgres',
    pwd = 'postgres',
    host = 'localhost', 
    port = '5432', 
    dbname = 'testdb'
    )
```
Saving a scenario to the database is done via the `write_to_db` funtion:
```python
write_to_db( connect, scenario )
```
Similarly, reading a scenario from the database is done with the help of the `read_from_db` function:
```python
scenario = read_from_db(
    connect,
    scenario_name = 'TestScenario'
    )
```

