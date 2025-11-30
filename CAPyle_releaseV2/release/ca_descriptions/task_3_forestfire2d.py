# Name: Task 1 and Task 2 CA
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
CHAPARRAL_FUEL = 3
FOREST_FUEL = 7
CANYON_FUEL = 1
CHAPARRAL_IGNITION_PROBABILITY = -0.8
FOREST_IGNITION_PROBABILITY = -0.94
CANYON_IGNITION_PROBABILITY = 0.5

# Constant Parmeters that can be overwritten
# when called through test rig
WIND_ENABLED = True
WIND_DIRECTION = random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
# A character that represents the wind direction
# i.e. 'N' is North, 'NW' is North West, 'E' is East etc. 
WATER_MODE = 'FIXED' # RANDOM or FIXED
STARTING_LOCATION = (50, 50)  

# For probability functions
C1 = 0.045
C2 = 0.131
WIND_SPEED = 18
BASE_PROBABILITY = 0.58

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


def generate_initial_map(water_placement=None):

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
    
    if water_placement is None:
      if WATER_MODE == 'RANDOM':
          # Set random line of water on map
          line_length_km = 12.5   # along the long side
          line_width_km  = 1.0    # thickness of the line
          
          # choose random orientation, horiztontal or vertical
          orientation = random.choice(['H', 'V'])
          orientation = 'H'  # for testing purposes, fix to horizontal

          # horizontal line orientation
          if orientation == 'H':
              # Horizontal line: long in x, thin in y
              y0 = random.uniform(0, 50 - line_width_km)
              y1 = y0 + line_width_km

              x0 = random.uniform(0, 50 - line_length_km)
              x1 = x0 + line_length_km

              initial_map[transform_y(y1):transform_y(y0), transform_x(x0):transform_x(x1)] = 3

          # vertical line orientation
          # else:
          #     # vertical line, long in y and thin in x
          #     x0 = random.uniform(0, 50 - line_width_km)
          #     x1 = x0 + line_width_km

          #     y0 = random.uniform(0, 50 - line_length_km)
          #     y1 = y0 + line_length_km

          #     initial_map[transform_y(y1):transform_y(y0),transform_x(x0):transform_x(x1)] = 3
      elif WATER_MODE == 'FIXED':
          
          # add specific lines of water in locations deemed most effective to stop fire, chooses one at random
          water_lines = [
              # (y_top, y_bottom, x_left, x_right)
              (15, 14, 0,   12.5),  # left of green forest (at the bottom)
              (45, 44, 0,   12.5),  # left of green forest (at the top)
              (18, 17, 25,  37.5),  # underneath canyon
              (11, 10, 10,  22.5),  # above town
          ]

          y_top, y_bottom, x_left, x_right = random.choice(water_lines)
          
          # for testing purposes vvvvvvvv, change water_lines(x) to choose specific location, comment out when not in use
          # y_top, y_bottom, x_left, x_right = water_lines[2]

          initial_map[transform_y(y_top):transform_y(y_bottom), transform_x(x_left):transform_x(x_right)] = 3
    else:
        y_top, y_bottom, x_left, x_right = water_placement
        initial_map[transform_y(y_top):transform_y(y_bottom), transform_x(x_left):transform_x(x_right)] = 3
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
    config.title = "Forest Fire - \n Water splash simulation" 
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

    if hasattr(config, 'water_placement'):
        config.initial_grid = generate_initial_map(config.water_placement)  # terrain_map
    else:
        config.initial_grid = generate_initial_map()
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

def prob_wind(angle, c_1=C1, wind_speed=WIND_SPEED, c_2=C2):
    return np.exp(c_1 * wind_speed)*np.exp(wind_speed * c_2 * (np.cos(angle) - 1))

def prob_burn(p_veg, p_w, p_h=BASE_PROBABILITY):
    return p_h*(1+p_veg)*p_w

def transition_function(grid, neighbourstates, neighbourcounts, decaygrid, wind_dir, wind_enabled):
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    cartesian_angles = np.deg2rad(np.array([
        315, 0, 45,
        270,    90,
        225, 180, 135
    ]))

    wind = None
    if wind_enabled:
        wind = True
        wind_direction = wind_dir[0]
    else:
        wind = False

    prob_grid = np.zeros(grid.shape, dtype=float)
    prob_grid[(grid == 0) | (grid == 1) | (grid == 2)] = 1.0

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

    # First decay cells that are potentially burnt
    decayed_to_0 = decaygrid == 0
    decayed_and_chap = (grid == 6) & decayed_to_0
    decayed_and_forest = (grid == 7) & decayed_to_0
    decayed_and_canyon = (grid == 8) & decayed_to_0
    
    # Transfer burning land to burnt land
    grid[decayed_and_chap] = 9
    grid[decayed_and_forest] = 10
    grid[decayed_and_canyon] = 11

    # Decrease fuel to simulate burning time
    decaygrid[grid == 6] -= 1
    decaygrid[grid == 7] -= 1
    decaygrid[grid == 8] -= 1

    # For each cell we want the probability of it burning in the next step
    # A given cell gets ignited based on a combination p_burn of all of its neighbours
    # 1 - (1- p1) (1- p2) (1-p3)
    for wind_angle_idx, burning_dir in enumerate(burning_dirs):
        indices_of_burning_dir = np.where(burning_dir)
        terrain = grid[indices_of_burning_dir]
        p_veg = np.empty_like(terrain, dtype=float)
        p_veg[terrain == 0] = CHAPARRAL_IGNITION_PROBABILITY
        p_veg[terrain == 1] = FOREST_IGNITION_PROBABILITY
        p_veg[terrain == 2] = CANYON_IGNITION_PROBABILITY
        other = ~((terrain== 0) | (terrain == 1) | (terrain == 2))
        if other.any():
            p_veg[other] = 0.0

        angle_between = cartesian_angles[wind_angle_idx] - cartesian_angles[wind_direction]
        wind_prob = prob_wind(angle=angle_between)
        prob_grid[indices_of_burning_dir] *= (1.0-prob_burn(p_veg, wind_prob))
    
    nonzero = prob_grid != 0.0
    prob_grid[nonzero] = 1.0 - prob_grid[nonzero]

    random_grid = np.random.rand(200, 200)
  
    #grid[(grid == 6) | (grid == 7) | (grid == 8)] += 3
    grid[random_grid < prob_grid] += 6 # Ignite cells to be ignited
    
    # Burning neighbour AND TOWN
    grid[((neighbourcounts[6] > 0) | (neighbourcounts[7] > 0)
          | (neighbourcounts[8] > 0)) & (grid == 4)] = 12

    if random.random() < 0.004:    
        if wind_dir[0] == 0:
            wind_dir[0] = wind_dir[0] + 1
        elif wind_dir[0] == 7:
            wind_dir[0] = wind_dir[0] - 1
        else: 
            wind_dir[0] = wind_dir[0] + random.choice([-1, 1])

        print(wind_dir[0], " new wind dir")
        print("Changed wind dir")
    
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
    init = config.initial_grid

    decaygrid[init == 0] = CHAPARRAL_FUEL  # Chap fuel
    decaygrid[init == 1] = FOREST_FUEL  # Forest fuel
    decaygrid[init == 2] = CANYON_FUEL  # Canyon fuel

    # This code enables us to run the program without GUI for different
    # Starting locations and wind directions
    if hasattr(config, 'wind_direction') and hasattr(config, 'starting_location'):
        wind_direction = [config.wind_direction]

    else:
        wind_direction = [{
        'NW': 0,
        'N': 1,
        'NE': 2,
        'W': 3,
        'E': 4,
        'SW': 5,
        'S': 6,
        'SE': 7
        }[WIND_DIRECTION]]
        config.starting_location = STARTING_LOCATION

    config.initial_grid[transform_y(config.starting_location[1]), transform_x(
            config.starting_location[0])] = 5
    # set neighbours of starting location to burning (6) with bounds checking
    sx = transform_x(config.starting_location[0])
    sy = transform_y(config.starting_location[1])
    rows, cols = config.grid_dims
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = sy + dy, sx + dx
            if 0 <= ny < rows and 0 <= nx < cols and config.initial_grid[ny, nx] < 4:
                config.initial_grid[ny, nx] = 6
    grid = Grid2D(config, (transition_function, decaygrid,
                  wind_direction, WIND_ENABLED))
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
