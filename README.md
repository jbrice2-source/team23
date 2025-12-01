Team 23 Project

# Description

This is an adapted GoL 2D Cellular Automata to simulate forest fires.

To there are 2 main ways to run our simulation:
- Loading the descriptions through the GUI
- Running the automated testrig

# Loading Descriptions Through GUI

```bash
# Change into correct directory
cd CAPyle_releaseV2/release/
# Run main script, you may need to change python3 to your system's alias.
python3 main.py
```
1. Once the GUI is open, at the top left of the GUI, navigate to:
2. `...\team23\CAPyle_releaseV2\release\ca_descriptions`
3. You can now choose a description to open, either `task_1_task_2_forestfire2d.py` or `task_3_forestfire2d.py`
4. To edit the number of generations, see the left side of the GUI
5. To setup the simulation, either click `Simulation > Run Simulation` which is at top left of the GUI, or `Apply configuration & run CA`
6. You can now press the `Play` button to start the simulation
7. To edit the playback speed of the simulation, move the FPS slider

# Running Automated Test Rig

```bash
# Change into correct directory
cd CAPyle_releaseV2/release/
# Run main script, you may need to change python3 to your system's alias.
python3 testrig.py
```

# Changing the Constants

To change constants such as 
`FOREST_IGNITION_PROBABILITY`

1. Navigate to `...\team23\CAPyle_releaseV2\release\ca_descriptions` on your IDE 
2. Open either `task_1_task_2_forestfire2d.py` or `task_3_forestfire2d.py`
3. Find the constant parameters comment at the top of the file 
```python
# Constant Parameters
```
4. Below this comment are the constant values, modify as required

# Modifiable constants
Fuel Values per Terrain
`CHAPARRAL_FUEL` - Fuel value for Chaparral
`FOREST_FUEL` - Fuel value for Dense Forests
`CANYON_FUEL` - Fuel value for Canyons of Scrublands

Ignition Probability per burnable terrain
`CHAPARRAL_IGNITION_PROBABILITY` - Ignition probability for Chaparral
`FOREST_IGNITION_PROBABILITY` - Ignition probability for Dense Forests
`CANYON_IGNITION_PROBABILITY` - Ignition probability for Canyons of Scrublands

Wind constants
`WIND_ENABLED` - True or False to enable wind effects
`WIND_DIRECTION` - Initial wind direction set as a character that corresponds to where the wind comes from i.e. 'N' for wind that blows from the North towards the South

Water intervention spawn type
`WATER_MODE` - Fixed or Random, for fixed positions of water intervention or random

Starting Location for Testrig simulations
`STARTING_LOCATION` - Starting location of an ignition source for testrigs. Format of (x, y) with each value in a range of 50 (km). Automatically translated to fit the higher resolution map

For probability functions
`C1`
`C2`
`WIND_SPEED`
`BASE_PROBABILITY`


