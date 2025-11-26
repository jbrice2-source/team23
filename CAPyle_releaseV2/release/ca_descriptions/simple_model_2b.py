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
import random
import numpy as np
import capyle.utils as utils
from capyle.ca import Grid2D, Neighbourhood, randomise2d



# Constant Parameters
CHAPARRAL_FUEL = 2000
FOREST_FUEL = 4000
CANYON_FUEL = 2000
CHAPARRAL_IGNITION_PROBABILITY = 0.8
FOREST_IGNITION_PROBABILITY = 0.8
CANYON_IGNITION_PROBABILITY = 0.8
WIND_ENABLED = True
WIND_DIRECTION = 1  # 1 is North
STARTING_LOCATION = (50, 50)  # x, y


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


def generate_initial_map():

    initial_map = np.zeros((200, 200))

    # When generating the map, make sure that
    #  the Y values go from higher to lower
    #  the X values go from lower to higher

    # MAP IS (Y,X)
    # Set Lakes
    initial_map[transform_y(40):transform_y(
        30), transform_x(17.5):transform_x(20)] = 3
    initial_map[transform_y(10):transform_y(
        7.5), transform_x(25):transform_x(40)] = 3

    # Set Forests
    initial_map[transform_y(45):transform_y(
        25), transform_x(5):transform_x(12.5)] = 1
    initial_map[transform_y(45):transform_y(
        42.5), transform_x(12.5):transform_x(20)] = 1
    initial_map[transform_y(25):transform_y(
        15), transform_x(5):transform_x(25)] = 1

    # Set Canyons
    initial_map[transform_y(40):transform_y(
        17.5), transform_x(35):transform_x(37.5)] = 2

    # Set Ignition points (Powerplant/Incinerator)
    # initial_map[transform_y(50), transform_x(5)] = 5 # powerplant
    # initial_map[transform_y(50), transform_x(50)] = 5 # incincerator

    # TESTING IGNITION POINTS
    # initial_map[transform_y(30), transform_x(25)] = 5
    # initial_map[transform_y(50), transform_x(0)] = 5

    # Set Town
    initial_map[transform_y(5+1.25):transform_y(5-1.25),
                transform_x(15-1.25):transform_x(15+1.25)] = 4

    return initial_map


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Simple Model 2"
    config.dimensions = 2
    config.num_generations = 1000
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
    # 12 - Burnt Town
    config.states = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0.75, 0.75, 0.0), (0.314, 0.384, 0.157), (0.988, 1, 0.004),
                           (0.0, 0.6, 1.0), (0.51, 0.027,
                                             0.631), (0.98, 0.145, 0.953),
                           (0.988, 0.616, 0.016), (0.688, 0.306,
                                                   0.016), (0.671, 0.004, 0.004),
                           (0.549, 0.549, 0.549), (0.322, 0.188, 0.012), (0.3, 0.3, 0.3), (0.4, 0.4, 0.4)]
    config.grid_dims = (200, 200)
    config.wrap = False

    config.initial_grid = generate_initial_map()  # terrain_map

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


def transition_function(grid, neighbourstates, neighbourcounts, decaygrid, wind_dir, wind_enabled):
    """Function to apply the transition rules
    and return the new grid"""
    # unpacking neighbour states
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    # enables or disables wind effects
    wind_direction = None
    if wind_enabled:
        wind = True
        wind_direction = wind_dir[0]

    # corresponds to the direction in the neighbourstates array (e.g. 0 is NW, 1 is N..)
    cartesian_angles_degrees = np.array([
        315, 0, 45,
        270,    90,
        225, 180, 135
    ])
    # converts cartesian_angles into a radians array
    cartesian_angles = np.deg2rad(cartesian_angles_degrees)

    burning_dirs = [
        (NW >= 6) & (NW <= 8),  # E.g all burning Northwesterly neighbours
        (N >= 6) & (N <= 8),
        (NE >= 6) & (NE <= 8),
        (W >= 6) & (W <= 8),
        (E >= 6) & (E <= 8),
        (SW >= 6) & (SW <= 8),
        (S >= 6) & (S <= 8),
        (SE >= 6) & (SE <= 8)
    ]

    # 200x200 burning probability array where we assign base probabilities on burnable
    # land types then skew for neighbours and wind direction
    prob_grid = np.zeros((200, 200))

    if wind == True:
        for affected_by_wind_idx, burning_dir in enumerate(burning_dirs):
            # Find all cells that have a burning dir niehgbour
            indices_of_burning_dir = np.where(burning_dir)
            # add the neighbour contribution
            prob_grid[indices_of_burning_dir] += 0.5 * np.cos(
                cartesian_angles[affected_by_wind_idx]-cartesian_angles[wind_direction])

    prob_grid = np.clip(prob_grid, 0.0, 1.0)

    # Ignite initial surrounding cells
    grid[(neighbourcounts[5] > 0) & (grid < 4)] = 6
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

    # Probability used to ignite cells
    random_grid = np.random.rand(200, 200)

    # rules and parameters that causes lands to burn
    burning_chap = (random_grid < (
        prob_grid * CHAPARRAL_IGNITION_PROBABILITY)) & chap
    burning_forest = (random_grid < (
        prob_grid * FOREST_IGNITION_PROBABILITY)) & forest
    burning_canyon = (random_grid < (
        prob_grid * CANYON_IGNITION_PROBABILITY)) & canyon
    grid[burning_chap] = 6
    grid[burning_forest] = 7
    grid[burning_canyon] = 8
    # Burning neighbour AND TOWN
    grid[((neighbourcounts[6] > 0) | (neighbourcounts[7] > 0)
          | (neighbourcounts[8] > 0)) & (grid == 4)] = 12
    # UNUSED DYNAMIC WIND
    # # Change wind direction with probability 0.05
    # if random.random() < 0.05:
    #     wind_dir[0] = random.randint(0, 7)
    #     print("Changed wind dir")

    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    # Also create a fuel decay grid to simulate burning times
    decaygrid = np.zeros(config.grid_dims)
    decaygrid[:, :] = -1  # Use -1 as a placeholder for non burning tiles

    # draws the terrain map
    init = generate_initial_map()

    decaygrid[init == 0] = CHAPARRAL_FUEL  # Chap fuel
    decaygrid[init == 1] = FOREST_FUEL  # Forest fuel
    decaygrid[init == 2] = CANYON_FUEL  # Canyon fuel
    # This code enables us to run the program without GUI for different
    # Starting locations and wind directions
    if hasattr(config, 'wind_direction') and hasattr(config, 'starting_location'):
        wind_direction = [config.wind_direction]
        config.initial_grid[transform_y(config.starting_location[1]), transform_x(
            config.starting_location[0])] = 5
    else:
        wind_direction = [WIND_DIRECTION]
        config.initial_grid[transform_y(
            STARTING_LOCATION[1]), transform_x(STARTING_LOCATION[0])] = 5

    grid = Grid2D(config, (transition_function, decaygrid,
                  wind_direction, WIND_ENABLED))
    timeline = grid.run()
    # from matplotlib import pyplot as plt
    # print(timeline[0])
    # plt.imshow(timeline[0])
    # plt.grid(markevery=1)
    # plt.show()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
