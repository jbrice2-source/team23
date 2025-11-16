# Name: Simple Model 2
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils
import numpy as np

import random

# Constant Parameters
CHAPARRAL_FUEL = 5
FOREST_FUEL = 20
CANYON_FUEL = 3
CHAPARRAL_IGNITION_PROBABILITY = 0.2
FOREST_IGNITION_PROBABILITY = 0.01
CANYON_IGNITION_PROBABILITY = 0.9

def generate_initial_map():

    def transform_y(num):
        result = (abs(50 - num) * 4)
        if int(result) > 0:
            result -= 1
        return int(result)
    def transform_x(num):
        result = (num * 4)
        if int(result) > 0:
            result -= 1
        return int(result)
    initial_map = np.zeros((200,200))
    # MAP IS (Y,X)
    #Set Lakes
    initial_map[transform_y(40):transform_y(30), transform_x(17.5):transform_x(20)] = 3
    initial_map[transform_y(10):transform_y(7.5), transform_x(25):transform_x(40)] = 3

    #Set Forests
    initial_map[transform_y(45):transform_y(25), transform_x(5):transform_x(12.5)] = 1
    initial_map[transform_y(45):transform_y(42.5), transform_x(12.5):transform_x(20)] = 1
    initial_map[transform_y(25):transform_y(15), transform_x(5):transform_x(25)] = 1

    #Set Canyons
    initial_map[transform_y(40):transform_y(17.5), transform_x(35):transform_x(37.5)] = 2

    #Set Ignition points (Powerplant/Incinerator)
    initial_map[transform_y(50), transform_x(5)] = 5
    initial_map[transform_y(50), transform_x(50)] = 5

    # TESTING IGNITION POINT IN THE CENTER
    initial_map[transform_y(30), transform_x(25)] = 5

    #Set Town
    initial_map[transform_y(5-1.25):transform_y(5+1.25), transform_x(15-1.25):transform_x(15+1.25)] = 4

    return initial_map


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Simple Model 2"
    config.dimensions = 2
    config.num_generations = 500
    # -- States
    # 0 - Chapparal
    # 1 - Dense forest
    # 2 - Canyon
    # 3 - Water
    # 4 - Town
    # 5 - Power Plant/Incinerator
    # 6 - Burning chaparral
    # 7 - Burning Forest
    # 8 - Burning Canyon
    # 9 - Burnt chaparral
    # 10 - Burnt Forest
    # 11 - Burnt Canyon
    config.states = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0.75, 0.75, 0.0),(0.314, 0.384, 0.157),(0.988, 1, 0.004), 
                           (0.0, 0.6, 1.0), (0.51, 0.027, 0.631),(0.98, 0.145, 0.953),
                           (0.988, 0.616, 0.016),(0.688, 0.306, 0.016), (0.671, 0.004, 0.004), 
                           (0.549, 0.549, 0.549),(0.322, 0.188, 0.012), (0.3,0.3,0.3)]
    config.grid_dims = (200,200)
    config.wrap = False

    config.initial_grid = generate_initial_map() #terrain_map
    
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # config.state_colors = [(0,0,0),(1,1,1)]
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def transition_function(grid, neighbourstates, neighbourcounts, decaygrid):
    """Function to apply the transition rules
    and return the new grid"""

    # unpacking neighbour states
    NW, N, NE, W, E, SW, S, SE = neighbourstates
    # enables or disables wind effects
    wind = True
    # corresponds to the direction in the neighbourstates array (e.g. 0 is NW, 1 is N..)
    wind_direction = 1 # testing wtih wind blowing from the North

    cartesian_angles_degrees = np.array([
        315, 0, 45,
        270,    90,
        225, 180, 135
    ])
    cartesian_angles = np.deg2rad(cartesian_angles_degrees)

    wind_array = np.zeros((8))
    affected_probability = 0

    burning_dirs = [
        (NW >= 6) & (NW <= 8),
        (N  >= 6) & (N  <= 8),
        (NE >= 6) & (NE <= 8),
        (W  >= 6) & (W <= 8),
        (E  >= 6) & (E <= 8),
        (SW >= 6) & (SW <= 8),
        (S  >= 6) & (S <= 8),
        (SE >= 6) & (SE <= 8)
    ]

    # creates a shifted array where the prevailing wind direction is equal to 0 degrees, 
    # so that all other angles are within a range of 0-360, with 180 being the opposite direction
    if wind == True:
        affected_by_wind = [cartesian_angles[(wind_direction + i) % len(cartesian_angles)] for i in range(len(cartesian_angles))]
        # uses this function so that the selected wind direction is weakest (because fire struggles to spread in the direction the wind is blowing)
        # and is strongest in the direction the wind is blowing from
    # use negative cos as it's -1 at origin, +1 at 180
    
    if wind == True:
        for i in range(len(neighbourstates)):
            near_burning = burning_dirs[i]  
            wind_array[i] = np.where(near_burning, -np.cos(affected_by_wind[i]), 0)
                ##wind_array[i] = -np.cos(affected_by_wind[i])
            print("Wind Array: position ", i, " ", wind_array[i])
            # is_burning = (neighbourstates[i] >= 5) & (neighbourstates[i] <= 8)
            # if (is_burning):
            #     wind_array[i] = -np.cos(affected_by_wind[i])
            # else:
        #     wind_array[i] = 0
            
    affected_probability = np.sum(wind_array)
    print(affected_probability)

    # Ignite initial surrounding cells
    grid[neighbourcounts[5] > 0] = 6 

    # Mask out Chapparal, Forest and Canyon
    chap = (grid == 0)
    forest = (grid == 1)
    canyon = (grid == 2)

    # Decrease fuel to simulate burning time
    decaygrid[grid == 6] -= 1 
    decaygrid[grid == 7] -= 1
    decaygrid[grid == 8] -= 1
    
    # Find where fuel is burnt away
    decayed_to_0 = decaygrid == 0 
    decayed_and_chap = (grid == 6) & decayed_to_0
    decayed_and_forest = (grid == 7) & decayed_to_0
    decayed_and_canyon = (grid == 8) & decayed_to_0

    # Transfer burning land to burnt land
    grid[decayed_and_chap] = 9
    grid[decayed_and_forest] = 10
    grid[decayed_and_canyon] = 11

    chaparral_wind_probability = np.clip(CHAPARRAL_IGNITION_PROBABILITY+affected_probability, 0, 1)
    forest_wind_probability = np.clip(FOREST_IGNITION_PROBABILITY+affected_probability, 0, 1)
    canyon_wind_probability = np.clip(CANYON_IGNITION_PROBABILITY+affected_probability, 0, 1)

    lands = [chap, forest, canyon]
    probs = [
        [chaparral_wind_probability, 1-chaparral_wind_probability], 
        [forest_wind_probability, 1-forest_wind_probability], 
        [canyon_wind_probability, 1-canyon_wind_probability]
    ]
    
    burning_neighbours = neighbourcounts[6] + neighbourcounts[7] + neighbourcounts[8]
    
    for i in range(3):
        # Create mask for certain land type
        mask = lands[i] & (burning_neighbours > 0) 

        # Create Probability Boolean over these cells
        burn_mask = np.random.choice(a=[True, False], size=np.count_nonzero(mask), p=probs[i]) 

        # Find indices of these cells where it is true
        grid_indices = np.where(mask) 
        grid[grid_indices[0][burn_mask], grid_indices[1][burn_mask]] = i+6
    

    ## ASSUME THAT THE TRANSITION FUNCTION LOOKS AT A SINGLE POSITION IN THE GRID, ITS NEIGHBOURSTATES AND A COUNT OF THE STATES ITS IN
    ## CALCULATE HOW MANY OF THE NEIGHBOURS ARE BURNING, THEN APPLY A WEIGHT TO THAT NEIGHBOUR RELATIVE TO THE WIND DIRECTION
    ## THE PROBABILITY OF BURNING IS EQUAL TO HOW MANY OF THE NEIGHBOURS ARE BURNING AND IN WHICH NEIGHBOUR POSITION THEY'RE IN
    ## i.e IF THE THE WIND IS BLOWING FROM THE NORTH, THEN IF THE NEIGHBOUR IN THE NORTH IS BURNING, THAT'S A HIGH CHANCE OF BURNING
    ## IF THE NEIGHBOUR TO THE SOUTH IS BURNING, THAT'S A LOWERED CHANCE OF BURNING (BECAUSE THE FIRE SPREADS AGAINST THE WIND)

    # Ignite initial surrounding cells
    # grid[neighbourcounts[5] > 0] = 6 

    # # Mask out Chapparal, Forest and Canyon
    # chap = (grid == 0)
    # forest = (grid == 1)
    # canyon = (grid == 2)

    # # Decrease fuel to simulate burning time
    # decaygrid[grid == 6] -= 1 
    # decaygrid[grid == 7] -= 1
    # decaygrid[grid == 8] -= 1
    
    # # Find where fuel is burnt away
    # decayed_to_0 = decaygrid == 0 
    # decayed_and_chap = (grid == 6) & decayed_to_0
    # decayed_and_forest = (grid == 7) & decayed_to_0
    # decayed_and_canyon = (grid == 8) & decayed_to_0

    # # Transfer burning land to burnt land
    # grid[decayed_and_chap] = 9
    # grid[decayed_and_forest] = 10
    # grid[decayed_and_canyon] = 11

    # lands = [chap, forest, canyon]
    # probs = [
    #     [CHAPARRAL_IGNITION_PROBABILITY, 1-CHAPARRAL_IGNITION_PROBABILITY], 
    #     [FOREST_IGNITION_PROBABILITY, 1-FOREST_IGNITION_PROBABILITY], 
    #     [CANYON_IGNITION_PROBABILITY, 1-CANYON_IGNITION_PROBABILITY]
    # ]
    
    # burning_neighbours = neighbourcounts[6] + neighbourcounts[7] + neighbourcounts[8]
    
    # for i in range(3):
    #     # Create mask for certain land type
    #     mask = lands[i] & (burning_neighbours > 0) 

    #     # Create Probability Boolean over these cells
    #     burn_mask = np.random.choice(a=[True, False], size=np.count_nonzero(mask), p=probs[i]) 

    #     # Find indices of these cells where it is true
    #     grid_indices = np.where(mask) 
    #     grid[grid_indices[0][burn_mask], grid_indices[1][burn_mask]] = i+6
    
    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    # Also create a fuel decay grid to simulate burning times
    decaygrid = np.zeros(config.grid_dims)
    decaygrid[:, :] = -1 # Use -1 as a placeholder for non burning tiles
    init = generate_initial_map()
    decaygrid[init == 0] = CHAPARRAL_FUEL # Chap fuel
    decaygrid[init == 1] = FOREST_FUEL # Forest fuel
    decaygrid[init == 2] = CANYON_FUEL # Canyon fuel
    grid = Grid2D(config, (transition_function, decaygrid))
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
